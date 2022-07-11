import argparse
from curses.ascii import FS
from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import POS_UNIT, ANG_UNIT
from raya.exceptions import RayaNavNotNavigating
import matplotlib.pyplot as plt


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.get_args()
        self.nav = await self.enable_controller('navigation')        
        self.log.info((f'Setting map: {self.map_name}. '
                       'Waiting for the robot to get localized'))
        if not await self.nav.set_map(self.map_name, 
                                      wait_localization=True, 
                                      timeout=3.0):
            self.log.info((f'Robot couldn\'t localize itself'))
            self.finish_app()
            return

        self.goal_zone = self.zone_name
        self.log.warn(f'New goal received zone {self.goal_zone}')
        await self.nav.navigate_to_zone( 
            zone_name=self.goal_zone,
            to_center=self.go_center,
            callback_feedback = self.cb_nav_feedback,
            callback_finish = self.cb_nav_finish,
            wait=False,
        )

    
    def cb_nav_finish(self, error, error_msg):
        print(f'cb_nav_finish {error} {error_msg}')
        self.finish_app()


    def cb_nav_feedback(self, state, distance_to_goal, speed):
        print(f'cb_nav_feedback {state} {distance_to_goal} {speed}')


    async def loop(self):
        if await self.nav.is_in_zone(zone_name=self.goal_zone):
            self.log.warn(f'Robot in zone')
        else:
            self.log.info((f'Robot not in zone'))
        await self.sleep(0.3)


    async def finish(self):
        try:
            await self.nav.cancel_navigation()
        except RayaNavNotNavigating:
            pass
        self.log.info('Finish app called')


    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-m', '--map-name',
                            type=str,
                            default='', required=True,
                            help='Map name')
        parser.add_argument('-z', '--zone-name',
                            type=str,
                            default='room1', required=False,
                            help='Zone name')
        parser.add_argument('-c', '--go-center', action='store_true', 
                            help='Spins while scanning')

        args = parser.parse_args()

        self.map_name = args.map_name
        self.zone_name = args.zone_name
        self.go_center = args.go_center


