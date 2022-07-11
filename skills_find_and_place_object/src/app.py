# Common Imports
import json
import cv2
import argparse

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
from raya.controllers.motion_controller import MotionController
from raya.controllers.cv_controller import DetectionObjectsHandler
from raya.controllers.navigation_controller import NavigationController
from raya.enumerations import POS_UNIT
from raya.tools.image import show_image
from raya.exceptions import RayaCVAlreadyEnabledType
from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import POS_UNIT, ANG_UNIT
from raya.exceptions import RayaNavNotNavigating


OBJECT_ZONES = {'kitchen': ['cup', 'bottle'], 'room01': []}


class RayaApplication(RayaApplicationBase):
    async def setup(self):
        self.arrived = False
        self.grasped = False
        self.arm_predefined = 'right_arm'
        self.retries = 0
        self.max_tries = 3
        self.detection = []
        self.objets_to_clean = []
        self.model_name = 'coral_efficientdet_lite0_320_coco'
        self.location_name2 = 'kitchen'
        self.predefined_pose_nav = 'nav_with_object2'
        self.predefined_pose_pre_pick = 'pre_step_3'
        self.predefined_pose_home = 'right_arm_home'
        self.point = [-2.18, 0.63, 0.8]
        self.get_args()
        self.cameras: CamerasController = await self.enable_controller('cameras')
        self.cv: CVController = await self.enable_controller('cv')
        self.motion: MotionController = await self.enable_controller('motion')
        self.nav: NavigationController = await self.enable_controller('navigation')
        self.gsp = await self.enable_controller('grasping') 
        self.arms = await self.enable_controller("arms")  
        await self.cameras.enable_color_camera(self.camera_name)
        self.log.info((f'Setting map: {self.map_name}. '
                       'Waiting for the robot to get localized'))
        if not await self.nav.set_map(self.map_name, 
                                      wait_localization=True, 
                                      timeout=3.0):
            self.log.info((f'Robot couldn\'t localize itself'))
            self.finish_app()

        self.log.info(f'Using map \'{self.map_name}\'')
        self.status = await self.nav.get_status()
        self.log.info(f'status: {self.status}')
        self.location = await self.nav.get_location(self.location_name, POS_UNIT.PIXEL)
        goal_x, goal_y, goal_yaw = self.location['x'], self.location['y'], 0.0
        self.log.warn(f'New goal received {goal_x, goal_y, goal_yaw}')
        await self.nav.navigate_to_location( 
            zone_name= self.location_name,
            callback_feedback = self.cb_nav_feedback,
            callback_finish = self.cb_nav_finish,
            wait=False,
        )
    
    def cb_nav_finish(self, error, error_msg):
        print(f'cb_nav_finish {error} {error_msg}')
        self.arrived = True
        # self.finish_app()


    def cb_nav_feedback(self, state, distance_to_goal, speed):
        print(f'cb_nav_feedback {state} {distance_to_goal} {speed}')


    def cb_object_detected(self, detection):
        self.detection = detection


    def callback_color_frame(self, img):
        detections = self.detector.get_current_detections()
        detection_names = []
        for detection in detections:
            img = cv2.rectangle(img, 
                                (detection['x_min'], detection['y_min']), 
                                (detection['x_max'], detection['y_max']), 
                                (0, 255, 0), 
                                2)
            img = cv2.putText(img, detection['object_name'], (detection['x_min'], detection['y_min'] - 5), cv2.FONT_HERSHEY_SIMPLEX,
			0.5, (0, 0, 255), 2)
            detection_names.append(detection['object_name'])
        self.log.info(f'Detections: {detection_names}')
        show_image(img, 'Video from Gary\'s camera', scale = 0.4)


    def cb_grasping_pick_finish(self, error, error_msg, result):
        self.grasped = True
        if error != 0:
            self.log.info(f'error: {error} {error_msg}')
            self.finish_app()
        self.arm = str(result['arm_pick'])
        self.real_height = result['height_object']
        self.log.info(f"Object height: {str(result['height_object'])}")
        self.log.info(f"Arm: {str(result['arm_pick'])}")
        self.log.info('Finish picking object')


    def cb_grasping_pick_feedback(self, state):
        self.log.info(f'State:  {state}')


    def cb_grasping_place_finish(self, error, error_msg):
        self.grasped = True
        if error != 0:
            self.log.info(f'error: {error} {error_msg}')
            self.finish_app()
        self.log.info('Finish place object')


    def cb_grasping_place_feedback(self, state):
        self.log.info(f'State:  {state}')


    def check_predefined_pose(self, pose):
        if not pose in self.arms.get_list_predefined_poses(
            self.arm_predefined
        ):
            self.list_predefined_poses()
            raise ValueError(
                f"the predefined_pose {pose} is not avaliable for this arm"
            )


    async def execute_predefined_pose(self, predefined_pose: str):
        print(f"\n Start the execution of the predefined pose {predefined_pose}\n")

        await self.arms.set_predefined_pose(
            self.arm_predefined,
            predefined_pose,
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            wait=True,
        )

    def callback_feedback(self, arg1, arg2):
        self.log.info(f"ARM:{arg1} PERCENTAGE:{arg2:.2f}")

    def callback_finish(self, error, error_msg):
        if error == 0:
            self.log.info('Predefined pose finished')
        else:
            self.log.info(f'Predefined pose failed, error {error}')
            self.finish_app()


    async def loop(self):
        if self.arrived:
            try:
                self.log.info('Enabling model')
                self.detector: DetectionObjectsHandler = \
                                await self.cv.enable_model(model='detectors',
                                type='object',
                                name= self.model_name,
                                source=self.camera_name,
                                model_params = {'depth': True})
                self.log.info('Model and camera enabled')
            except RayaCVAlreadyEnabledType:
                await self.cv.disable_model(model='detectors',type='object')
                self.log.info('Run again...')
                self.finish_app()
                return
            # Create listeners
            self.cameras.create_color_frame_listener(
                                            camera_name=self.camera_name,
                                            callback=self.callback_color_frame)            
            self.log.info(f'Looking for objects')
            await self.motion.rotate(angle=-360.0, angular_velocity=30.0, wait=False)


            await self.detector.find_objects([self.object_name], callback=self.cb_object_detected)       
            while (not self.detection) and (self.motion.is_moving()):
                await self.sleep(0.1)

            self.detector.cancel_find_objects()

            if self.motion.is_moving():
                await self.motion.cancel_motion()

            if not self.detection:
                self.log.error(f'Object {self.object_name} not found')
                self.finish_app()
                return

            await self.sleep(0.5)
            # VERIFY
            self.detection = await self.detector.find_objects([self.object_name], wait=True, timeout=0.5)
            if not self.detection:
                self.log.error(f'Object {self.object_name} not found')
                self.finish_app()
                return


            self.check_predefined_pose(self.predefined_pose_pre_pick)
            await self.execute_predefined_pose(self.predefined_pose_pre_pick)
            await self.sleep(0.5)

            obj_x = self.detection[0]['center_point_map'][0]
            obj_y = self.detection[0]['center_point_map'][1]

            self.log.info(f'Object {self.object_name} found!!')
            self.log.info(f'Object position in the map: x: {obj_x} y: {obj_y}')
            
            while self.retries < self.max_tries:
                try:
                    await self.nav.navigate_close_to_position(x=obj_x, y=obj_y, 
                                                            pos_unit=POS_UNIT.METERS,
                                                            wait=True)
                except:
                    self.retries += 1
                else:
                    self.log.info(f'Navigation succes!!')
                    break

            await self.gsp.pick_object(detector_model = self.model_name, 
                    source = self.camera_name, object_name = self.object_name, 
                    arms = [self.arm_predefined],
                    callback_feedback = self.cb_grasping_pick_feedback,
                    callback_finish = self.cb_grasping_pick_finish,
                    wait=False,
                )
            self.log.info(f'Pick Object started...')

            while (not self.grasped):
                await self.sleep(0.1)
            self.log.info('Moving backward 0.5 meters at 0.3 m/s')
            await self.motion.move_linear(distance=-0.5, x_velocity=0.3)
            while self.motion.is_moving(): await self.sleep(0.1)
            self.log.info('Motion command finished'); self.log.info('')

            self.check_predefined_pose(self.predefined_pose_nav)
            await self.execute_predefined_pose(self.predefined_pose_nav)
            await self.sleep(0.5)

            self.arrived = False
            await self.nav.navigate_to_location( 
                zone_name= self.location_name2,
                callback_feedback = self.cb_nav_feedback,
                callback_finish = self.cb_nav_finish,
                wait=False,
            )

            while not self.arrived:
                await self.sleep(0.1)

            self.check_predefined_pose(self.predefined_pose_pre_pick)
            await self.execute_predefined_pose(self.predefined_pose_pre_pick)
            await self.sleep(0.5)

            self.log.info(f'Object position in the map: x: {self.point[0]} y: {self.point[1]}')
            while self.retries < self.max_tries:
                try:
                    await self.nav.navigate_close_to_position(x=self.point[0], y =self.point[1], 
                                                            pos_unit=POS_UNIT.METERS,
                                                            wait=True)
                except:
                    self.retries += 1
                else:
                    self.log.info(f'Navigation succes!!')
                    break
            self.log.info(f'Placing Object')
            self.grasped = False
            await self.gsp.place_object_with_point(point_to_place = self.point, 
                height_object = self.real_height, arm = self.arm_predefined,
                callback_feedback = self.cb_grasping_place_feedback,
                callback_finish = self.cb_grasping_place_finish,
                wait=False,
            )
            while (not self.grasped):
                await self.sleep(0.1)
            self.log.info(f'Place Object with point finished...')
            self.log.info('Moving backward 0.5 meters at 0.3 m/s')
            await self.motion.move_linear(distance=-0.3, x_velocity=0.3)
            while self.motion.is_moving(): await self.sleep(0.1)
            self.log.info('Motion command finished'); self.log.info('')
            self.check_predefined_pose(self.predefined_pose_home)
            await self.execute_predefined_pose(self.predefined_pose_home)
            await self.sleep(0.5)

            self.finish_app()

    async def finish(self):
        try:
            await self.nav.cancel_navigation()
            if self.camera_name != None:
                self.log.info('Disabling model...')
                await self.cv.disable_model(model='detectors',type='object')
                self.log.info('Disabling camera...')
                self.cameras.disable_color_camera(self.camera_name)
        except RayaNavNotNavigating:
            pass
        self.log.info('Finish app called')


    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-m', '--map-name',
                            type=str,
                            default='', required=True,
                            help='Map name')
        parser.add_argument('-l', '--location-name',
                            type=str,
                            default='kitchen', required=False,
                            help='Location name')
        parser.add_argument('-o', '--object-name',
                            type=str,
                            default='', required=True,
                            help='Object name')
        parser.add_argument('-c', '--camera-name',
                            type=str,
                            default='', required=True,
                            help='Camera name')
        args = parser.parse_args()

        self.map_name = args.map_name
        self.location_name = args.location_name
        self.object_name = args.object_name
        self.camera_name = args.camera_name
