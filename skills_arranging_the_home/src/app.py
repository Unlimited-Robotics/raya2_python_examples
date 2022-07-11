# Common Imports
import cv2
import argparse
import numpy as np

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
from raya.controllers.cv_controller import DetectionObjectsHandler
from raya.controllers.grasping_controller import GraspingController
from raya.controllers.arms_controller import ArmsController
from raya.controllers.motion_controller import MotionController
from raya.controllers.navigation_controller import NavigationController
from raya.controllers.navigation_controller import POS_UNIT
from raya.tools.image import show_image
from raya.exceptions import RayaCVAlreadyEnabledType
from raya.application_base import RayaApplicationBase
from raya.exceptions import RayaNavNotNavigating


OBJECT_ZONES = {'kitchen': ['cup', 'bottle'], 'room01': []}


class RayaApplication(RayaApplicationBase):
    async def setup(self):

        ## Common Variables
        self.arrived = False
        self.grasped = False
        self.retries = 0
        self.max_tries = 3
        self.detection = []
        self.arms_dict = {'right_arm' : [False, 0.0], 'left_arm' : [False, 0.0]}
        self.objets_to_clean = {}
        self.model_name = 'coral_efficientdet_lite0_320_coco'
        self.location_name2 = 'kitchen'
        self.predefined_pose_nav = 'nav_with_object2'
        self.predefined_pose_pre_pick = 'pre_step_3'
        self.predefined_pose_home = 'right_arm_home'
        self.point = [-2.6, 0.6, 0.85]

        ## Get Arguments
        self.get_args()

        ## Initialize neccesary Controllers
        self.cameras: CamerasController = await self.enable_controller('cameras')
        self.cv: CVController = await self.enable_controller('cv')
        self.motion: MotionController = await self.enable_controller('motion')
        self.nav: NavigationController = await self.enable_controller('navigation')
        self.gsp: GraspingController = await self.enable_controller('grasping') 
        self.arms: ArmsController = await self.enable_controller("arms") 

        ## Enable Color Camera 
        await self.cameras.enable_color_camera(self.camera_name)

        ## Set navigation variables
        self.log.info((f'Setting map: {self.map_name}. '
                       'Waiting for the robot to get localized'))
        if not await self.nav.set_map(self.map_name, 
                                      wait_localization=True, 
                                      timeout=3.0):
            self.log.info((f'Robot couldn\'t localize itself'))
            self.finish_app()
        self.status = await self.nav.get_status()
        self.log.info(f'status: {self.status}')


    ## Callbacks Navigation
    def cb_nav_finish(self, error, error_msg):
        print(f'cb_nav_finish {error} {error_msg}')
        self.arrived = True


    def cb_nav_feedback(self, state, distance_to_goal, speed):
        print(f'cb_nav_feedback {state} {distance_to_goal} {speed}')


    ## Callbacks Object Detection
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
            self.check_objects_to_clean(detection)
        show_image(img, 'Video from Gary\'s camera', scale = 0.5)


    ## Grasping Pick Callbacks
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


    ## Grasping Place Callbacks
    def cb_grasping_place_finish(self, error, error_msg):
        self.grasped = True
        if error != 0:
            self.log.info(f'error: {error} {error_msg}')
            self.finish_app()
        self.log.info('Finish place object')


    def cb_grasping_place_feedback(self, state):
        self.log.info(f'State:  {state}')


    ## Arms Callbacks
    def callback_arm_feedback(self, arg1, arg2):
        self.log.info(f"ARM:{arg1} PERCENTAGE:{arg2:.2f}")


    def callback_arm_finish(self, error, error_msg):
        if error == 0:
            self.log.info('Predefined pose finished')
        else:
            self.log.info(f'Predefined pose failed, error {error}')
            self.finish_app()


    ## Common Functions
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
        parser.add_argument('-c', '--camera-name',
                            type=str,
                            default='', required=True,
                            help='Camera name')
        args = parser.parse_args()

        self.map_name = args.map_name
        self.location_name = args.location_name
        self.camera_name = args.camera_name


    def check_objects_to_clean(self, detection):
        if detection['object_name'] not in self.objets_to_clean:
            self.objets_to_clean[detection['object_name']] = [detection['center_point_map']]
        else:
            add_obj = True
            for objects in self.objets_to_clean[detection['object_name']]:
                p1 = np.array(detection['center_point_map'])
                p2 = np.array(objects)
                squared_dist = np.sum((p1-p2)**2, axis=0)
                dist = np.sqrt(squared_dist)
                if dist < 1:
                    add_obj = False
            if add_obj and detection['object_name'] in OBJECT_ZONES[self.location_name]:
                self.objets_to_clean[detection['object_name']].append(detection['center_point_map'])


    def check_predefined_pose(self, pose, arm):
        if not pose in self.arms.get_list_predefined_poses(
            arm
        ):
            raise ValueError(
                f"the predefined_pose {pose} is not avaliable for this arm"
            )


    async def execute_predefined_pose(self, predefined_pose: str, arm):
        print(f"\n Start the execution of the predefined pose {predefined_pose}\n")

        await self.arms.set_predefined_pose(
            arm,
            predefined_pose,
            callback_feedback=self.callback_arm_feedback,
            callback_finish=self.callback_arm_finish,
            wait=True,
        )


    def get_available_arms(self):
        arms = []
        for arm in self.arms_dict:
            if not self.arms_dict[arm][0]:
                arms.append(arm)
        return arms


    async def go_to_pose(self, pose, arm):
        self.check_predefined_pose(pose, arm)
        await self.execute_predefined_pose(pose, arm)
        await self.sleep(0.5)


    async def loop(self):
        ## Get location Point
        self.log.info(f'Goint to {self.location_name}')

        ## Navigate to location
        await self.nav.navigate_to_location( 
            zone_name= self.location_name,
            callback_feedback = self.cb_nav_feedback,
            callback_finish = self.cb_nav_finish,
            wait=False,
        )
        while not self.arrived: await self.sleep(0.1)
        
        ## Enable detection model
        try:
            self.log.info('Enabling object detection model')
            self.detector: DetectionObjectsHandler = \
                            await self.cv.enable_model(model='detectors',
                            type='object',
                            name= self.model_name,
                            source=self.camera_name,
                            model_params = {'depth': True})
            
        except RayaCVAlreadyEnabledType:
            await self.cv.disable_model(model='detectors',type='object')
            self.log.info('Run again...')
            self.finish_app()
            return

        # Create camera listener
        self.cameras.create_color_frame_listener(
                                        camera_name=self.camera_name,
                                        callback=self.callback_color_frame)  
        self.log.info('Model and camera enabled')          
        self.log.info(f'Looking for objects')

        ## Rotate 360 degrees
        await self.motion.rotate(angle=-360.0, angular_velocity=30.0, wait=False)
        while self.motion.is_moving(): await self.sleep(0.1)
        if self.motion.is_moving(): await self.motion.cancel_motion()

        ## Disable Camera
        self.log.info('Disabling camera...')
        self.cameras.disable_color_camera(self.camera_name)

        ## Check Objects to clean
        if len(self.objets_to_clean) > 0:

            # ## Move arms to pre_setep3 pose
            # for arm in self.arms_dict:
            #     await self.go_to_pose(self.predefined_pose_pre_pick, arm)
                
            ## Loop in objects to clean    
            for obj in self.objets_to_clean:
                for point in self.objets_to_clean[obj]:

                    ## Get X and Y point
                    obj_x = point[0]
                    obj_y = point[1]
                    self.log.info(f'Object position in the map: x: {obj_x} y: {obj_y}')

                    ## Navigate To Point
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
                    
                    ## Obtain available arms to pick
                    available_arms = self.get_available_arms()

                    ## Try to pick object
                    self.grasped = False
                    await self.gsp.pick_object(detector_model = self.model_name, 
                        source = self.camera_name, object_name = obj, 
                        arms = available_arms,
                        callback_feedback = self.cb_grasping_pick_feedback,
                        callback_finish = self.cb_grasping_pick_finish,
                        wait=False,
                    )
                    self.log.info(f'Pick Object started...')     
                    while (not self.grasped):await self.sleep(0.1) 

                    ## Update arms state
                    self.arms_dict[self.arm][0] = True
                    self.arms_dict[self.arm][1] = self.real_height

                    ## Move backward 0.3 meters at 0.3 m/s
                    self.log.info('Moving backward 0.3 meters at 0.3 m/s')
                    await self.motion.move_linear(distance=-0.3, x_velocity=0.3)
                    while self.motion.is_moving(): await self.sleep(0.1)
                    self.log.info('Motion command finished')

                    ## Move arm to navigate pose
                    await self.go_to_pose(self.predefined_pose_nav, self.arm)
        else:
            self.log.error(f'Nothing to clean')
            self.finish_app()
            return
        
        ## Navigate to location
        self.arrived = False
        await self.nav.navigate_to_location( 
            zone_name= self.location_name2,
            callback_feedback = self.cb_nav_feedback,
            callback_finish = self.cb_nav_finish,
            wait=False,
        )
        while not self.arrived: await self.sleep(0.1)

        # ## Move arms to pre_place pose
        # for arm in self.arms_dict:
        #     await self.go_to_pose(self.predefined_pose_pre_pick, arm)

        ## Loop to check arms state
        for arms_place in self.arms_dict:

            ## If arm have an object
            if self.arms_dict[arms_place][0]:

                ## Navigate To Point
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

                ## Place Object    
                self.log.info(f'Placing Object')
                self.grasped = False
                await self.gsp.place_object_with_point(point_to_place = self.point, 
                    height_object = self.arms_dict[arms_place][1], arm = arms_place,
                    callback_feedback = self.cb_grasping_place_feedback,
                    callback_finish = self.cb_grasping_place_finish,
                    wait=False,
                )
                while (not self.grasped): await self.sleep(0.1)
                self.log.info(f'Place Object with point finished...')

                ## Move point to place another object
                self.point[0] -= -0.25

                ## Move backward 0.3 meters at 0.3 m/s
                self.log.info('Moving backward 0.3 meters at 0.3 m/s')
                await self.motion.move_linear(distance=-0.3, x_velocity=0.3)
                while self.motion.is_moving(): await self.sleep(0.1)
                self.log.info('Motion command finished')
                
                ## Go to home pose
                await self.go_to_pose(f'{arms_place}_home', arms_place)

        ## Finish app
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



