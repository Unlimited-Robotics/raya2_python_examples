###### EXPECTED BEHAVIOUR ########
# This example should get the available cameras and enable the camera in zero position
# later it should show the cv models available to run and it must enable a object detection model
# finally it should get the data from the camera and open a window where show the image and the baunding boxes of each detection

# Common Imports
import json
import cv2
import argparse

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
from raya.tools.image import show_image


class RayaApplication(RayaApplicationBase):
    async def setup(self):
        self.log.info('Ra-Ya Py - Computer Vision Object Detection Example')

        # Get Arguments
        self.get_args()

        # Call Cameras Controller
        self.cameras: CamerasController = await self.enable_controller('cameras')
        self.available_cameras = self.cameras.available_color_cameras()
        self.log.info('Available cameras:')
        self.log.info(f'{self.available_cameras}')
        self.working_camera = None

        # If a camera name was set
        if self.camera != None:
            cams = set(self.available_cameras)
            if self.camera in cams:
                self.working_camera = self.camera
            else:
                self.log.info('Camera name not available')
                self.finish_app()
                return
        else:
            # If a camera name wasn't set it works with camera in zero position
            self.working_camera = self.available_cameras[0]

        # Enable camera
        await self.cameras.enable_color_camera(self.working_camera)

        # Computer Vision
        self.cv: CVController = await self.enable_controller('cv')

        # Get Available models to run
        self.available_models = self.cv.get_available_models()
        self.log.info('Available Computer Vision models:')

        # Pretty print
        self.log.info(json.dumps(self.available_models, indent=2))

        # Enable detector
        self.log.info('Enabling model...')
        self.detector = await self.cv.enable_model(model='detectors',type='object',
                                                      name=str(self.model),
                                                      source=self.working_camera,
                                                      model_params = {'depth': True}
                                                     )
        self.log.info('Model enabled')

        # Print objects detectables in the model
        self.log.info(f'Objects labels: {self.detector.get_objects_names()}')

        for object in self.finish_object:
            if object not in self.detector.get_objects_names():
                self.log.info((f'\'{self.finish_object}\' is not a valid'
                                           ' label for the current model'))
                self.finish_app()
                return
                
        # Create listeners
        self.cameras.create_color_frame_listener(
                                        camera_name=self.working_camera,
                                        callback=self.callback_color_frame)


    async def loop(self):
        self.log.info(f'Waiting for one of these objects: {self.finish_object}')
        resp = await self.detector.find_objects(self.finish_object, wait = True, timeout = self.duration)
        if not resp:
            self.log.info(f'Timer Finish!')
        else:
            self.log.info(f"Done! Object {resp[0]['object_name']} Found")
        self.finish_app()
        

    async def finish(self):
        if self.working_camera != None:
            self.log.info('Disabling model...')
            await self.cv.disable_model(model='detectors',type='object')
            self.log.info('Disabling camera...')
            self.cameras.disable_color_camera(self.working_camera)
        self.log.info('Ra-Ya application finished')


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
        #self.log.info(f'Detections: {detection_names}')
        show_image(img, 'Video from Gary\'s camera')

    
    def get_args(self):
        # Arguments
        parser = argparse.ArgumentParser(description='Computer vision example to detect specific objects non blockin and not blocking option',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("-m", "--model", help="object model name")
        parser.add_argument('-c', '--camera-name', type=str, 
                            help='name of camera to use')
        parser.add_argument("-f", "--finish-object",default=['book'],nargs='+', help="list of strings with the objects, when find one of those the program finish")
        parser.add_argument('-d',  '--duration', type=float, default=20.0,
                                               help='Scanning duration')
        parser.add_argument('-s', '--simulation', dest='simulation', action='store_true')
        args = parser.parse_args()
        self.model = args.model
        self.camera = args.camera_name
        self.finish_object = args.finish_object
        self.duration = args.duration
        self.sim = args.simulation
        # If Simulation
        if self.model == None:
            if self.sim:
                self.model = 'coral_efficientdet_lite0_320_coco'
            else:
                self.model = 'gpu_yolov5s_coco'
