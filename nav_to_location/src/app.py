import argparse
from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import POS_UNIT, ANG_UNIT
from raya.exceptions import RayaNavNotNavigating
import matplotlib.pyplot as plt


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.get_args()
        self.nav = await self.enable_controller('navigation')
        self.list_of_maps = await self.nav.get_list_of_maps()
        self.log.info(f'List of maps: {self.list_of_maps}')
        self.log.info((f'Setting map: {self.map_name}. '
                       'Waiting for the robot to get localized'))
        if not await self.nav.set_map(self.map_name, 
                                      wait_localization=True, 
                                      timeout=3.0):
            self.log.info((f'Robot couldn\'t localize itself'))
            self.finish_app()

        self.log.info(f'Using map \'{self.map_name}\'')
        self.status = await self.nav.get_status()
        self.log.info(f'status: {self.status}')
        self.location = await self.nav.get_location(self.location_name, POS_UNIT.PIXEL)
        goal_x, goal_y, goal_yaw = self.location['x'], self.location['y'], 0.0
        self.log.warn(f'New goal received {goal_x, goal_y, goal_yaw}')
        await self.nav.navigate_to_location( 
            zone_name= self.location_name,
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
        robot_position = await self.nav.get_position(
                    pos_unit = POS_UNIT.PIXEL, ang_unit = ANG_UNIT.RAD)
        #self.log.warn(f'Robot_position {robot_position}')


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
        parser.add_argument('-l', '--location-name',
                            type=str,
                            default='kitchen', required=False,
                            help='Location name')

        args = parser.parse_args()

        self.map_name = args.map_name
        self.location_name = args.location_name
