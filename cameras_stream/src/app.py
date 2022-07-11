import argparse

from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.tools.image import show_image


LOOP_PERIOD = 1.0


class RayaApplication(RayaApplicationBase):

    async def setup(self):

        # Get Arguments
        self.get_args()

        # Call Cameras Controller
        self.cameras: CamerasController = \
                                    await self.enable_controller('cameras')
        self.available_cameras = self.cameras.available_color_cameras()
        self.working_camera = None
        self.log.info('Available cameras:')
        self.log.info(f'  {self.available_cameras}')

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
            # self.working_camera = self.available_cameras[0]
            self.working_camera = 'head_front'

        # Enable camera
        self.log.info(f'Enabling camera \'{self.working_camera}\'...')
        await self.cameras.enable_color_camera(self.working_camera)
        self.log.info('Camera enabled')

        # If spin parameter was set 
        if self.spin_ena:
            # Call motion controller
            self.motion = await self.enable_controller('motion')
            await self.motion.set_velocity(x_velocity=0.0, y_velocity=0.0, 
                                           angular_velocity=-20.0, 
                                           duration=self.duration)
        self.time_counter = 0


    async def loop(self):
        # Wait for next frame in Camera
        img = await self.cameras.get_next_frame(self.working_camera)
        if img is not None:
            show_image(img, 'Video from Gary\'s camera', scale = 0.4)
        if self.spin_ena:
            if not self.motion.is_moving():
                self.finish_app()
        else:
            await self.sleep(1.0)
            self.time_counter += 1
            if self.time_counter >= self.duration:
                self.log.info('Counter Finish...')
                self.finish_app()
        

    async def finish(self):
        if self.working_camera != None:
            self.log.info('Disabling camera...')
            self.cameras.disable_color_camera(self.working_camera)
        if self.spin_ena and self.motion.is_moving():
            await self.motion.cancel_motion()


    def get_args(self):
        # Arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--camera-name', type=str, 
                            help='name of camera to use')
        parser.add_argument('-s', '--spin', action='store_true', 
                            help='Spins while scanning')
        parser.add_argument('-d', '--duration',
                            type=float, default=20.0,
                            help='Scanning duration')
        parser.set_defaults(feature=True)
        args = parser.parse_args()
        self.camera = args.camera_name
        self.spin_ena = args.spin
        self.duration = args.duration
        