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
        self.log.info(f'Enabling camera \'{self.working_camera}\'...')
        await self.cameras.enable_color_camera(self.working_camera)
        self.log.info('Camera enabled')
        if MOTION:
            self.motion = await self.enable_controller('motion')
            await self.motion.set_velocity(x=0.0, y=0.0, w=-0.5, duration=100.0)


    async def loop(self):
        img = await self.cameras.get_next_frame(self.working_camera)
        if img is not None:
            show_image(img, 'Video from Gary\'s camera', scale = 0.4)
        self.i += 1
        if self.i>500:
            self.finish_app()
        

    async def finish(self):
        self.cameras.disable_color_camera(self.working_camera)
        if MOTION:
            await self.motion.cancel_motion()