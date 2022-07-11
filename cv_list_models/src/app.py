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
        # Computer Vision
        self.cv: CVController = await self.enable_controller('cv')

        # Get Available models to run
        self.available_models = self.cv.get_available_models()
        self.log.info('Available Computer Vision models:')

        # Pretty print
        self.log.info(json.dumps(self.available_models, indent=2))


    async def loop(self):
        self.finish_app()
        

    async def finish(self):
        pass
