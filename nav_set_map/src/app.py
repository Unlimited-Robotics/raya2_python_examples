import argparse

from raya.controllers.motion_controller import MotionController
from raya.application_base import RayaApplicationBase
from raya.enumerations import ANG_UNIT

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        if not self.get_args():
            self.finish_app()
            return
        self.nav = await self.enable_controller('navigation')
        self.log.info((f'Setting map: {self.map_name}. '
                       'Waiting for the robot to get localized'))
        if not await self.nav.set_map(self.map_name, 
                                      wait_localization=True, 
                                      timeout=3.0):
            self.log.info(f'Robot couldn\'t localize itself')
        self.finish_app()

    
    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-m', '--map-name',
                            type=str, required=True,
                            help='Map name')
        try:
            args = parser.parse_args()
        except:
            return False
        self.map_name = args.map_name
        return True


    async def loop(self):
        self.finish_app()


    async def finish(self):
        pass
