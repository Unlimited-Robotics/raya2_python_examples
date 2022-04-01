import time

from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.tools.image import show_image

MOTION = True

class RayaApplication(RayaApplicationBase):
    async def setup(self):
        self.i = 0
        self.cameras: CamerasController = await self.enable_controller('cameras')
        self.available_cameras = self.cameras.available_color_cameras()
        self.log.info('Available cameras:')
        self.log.info(f'  {self.available_cameras}')
        self.working_camera = self.available_cameras[2]
        # Enable camera
        await self.cameras.enable_color_camera(self.working_camera)
        # Create listener
        self.cameras.create_color_frame_listener(
                                        camera_name=self.working_camera,
                                        callback=self.callback_color_frame)
        if MOTION:
            self.motion = await self.enable_controller('motion')
            await self.motion.set_velocity(x=0.0, y=0.0, w=-0.5, duration=100.0)


    async def loop(self):
        self.log.info('Doing other (non blocking) stuff')
        await self.sleep(1.0)
        self.i += 1
        if self.i>10.0:
            self.finish_app()
        

    async def finish(self):
        self.cameras.disable_color_camera(self.working_camera)
        if MOTION:
            await self.motion.cancel_motion()
        self.log.info('Ra-Ya application finished')


    def callback_color_frame(self, img):
        show_image(img, 'Video from Gary\'s camera', scale = 0.4)
