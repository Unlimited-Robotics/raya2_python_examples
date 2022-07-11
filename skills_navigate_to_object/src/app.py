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


class RayaApplication(RayaApplicationBase):
    async def setup(self):
        self.get_args()
        self.retries = 0
        self.max_tries = 3
        self.detection = []

        self.cameras: CamerasController = await self.enable_controller('cameras')
        self.cv: CVController = await self.enable_controller('cv')
        self.motion: MotionController = await self.enable_controller('motion')
        self.nav: NavigationController = await self.enable_controller('navigation')

        await self.cameras.enable_color_camera(self.camera_name)
        
        self.log.info((f'Setting map: {self.map_name}. '
                       'Waiting for the robot to get localized'))
        if not await self.nav.set_map(self.map_name, 
                                      wait_localization=True, 
                                      timeout=3.0):
            self.log.info(f'Robot couldn\'t localize itself')
            self.finish_app()
        else:
            self.log.info(f'Robot localized')
            self.log.info(f'')

        try:
            self.detector: DetectionObjectsHandler = \
                            await self.cv.enable_model(model='detectors',
                            type='object',
                            name='coral_efficientdet_lite0_320_coco',
                            source=self.camera_name,
                            model_params = {'depth': True})
        except RayaCVAlreadyEnabledType:
            await self.cv.disable_model(model='detectors',type='object')
            self.log.info('Run again...')
            self.finish_app()
            return



        self.log.info('Model and camera enabled')
                
        # Create listeners
        self.cameras.create_color_frame_listener(
                                        camera_name=self.camera_name,
                                        callback=self.callback_color_frame)


    async def loop(self):
        self.log.info(f'Looking for object {self.object_name}')
        await self.motion.rotate(angle=-90.0, angular_velocity=10.0, wait=False)
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
                self.finish_app()
                break
        self.finish_app()
        

    async def finish(self):
        self.log.info('Disabling model...')
        await self.cv.disable_model(model='detectors', type='object')
        self.log.info('Disabling camera...')
        self.cameras.disable_color_camera(self.camera_name)
        self.log.info('Ra-Ya application finished')

    
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
            detection_names.append(detection['object_name'])
        #self.log.info(f'Detections: {detection_names}')
        show_image(img, 'Video from Gary\'s camera')


    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-m', '--map-name',
                            type=str,
                            default='', required=True,
                            help='Map name')
        parser.add_argument('-o', '--object-name',
                            type=str,
                            default='', required=True,
                            help='Object name')
        parser.add_argument('-c', '--camera-name',
                            type=str,
                            default='', required=True,
                            help='Camera name')
        parser.add_argument('-d', '--model-name',
                            type=str,
                            default='', required=True,
                            help='AI model name')

        args = parser.parse_args()

        self.map_name = args.map_name
        self.object_name = args.object_name
        self.camera_name = args.camera_name
        self.model_name = args.model_name