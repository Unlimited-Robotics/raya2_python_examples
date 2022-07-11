from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.tools.image import show_image


LOOP_PERIOD = 1.0


class RayaApplication(RayaApplicationBase):

    async def setup(self):

        # Call Cameras Controller
        self.cameras: CamerasController = await self.enable_controller('cameras')
        self.available_cameras = self.cameras.available_color_cameras()
        self.working_camera = None
        self.log.info('Available cameras:')
        self.log.info(f'  {self.available_cameras}')


    async def loop(self):
        self.finish_app()
        

    async def finish(self):
        pass