import argparse
from pickle import FALSE
from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import POS_UNIT, ANG_UNIT
from raya.exceptions import RayaNavNotNavigating, RayaNavZoneAlreadyExist
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

        self.log.info(f'Using map \'{self.map_name}\'')
        zone_name = self.zone_name
        try:
            if not await self.nav.save_zone( 
                    zone_name=zone_name, 
                    points=[[280, 497],[280, 319],[427, 321],[426, 494]], 
                    pos_unit = POS_UNIT.PIXEL
                    ):
                self.log.info((f'Unable to save zone'))
                self.finish_app()
                return

            self.log.info((f'Zone saved succesfully'))
        except RayaNavZoneAlreadyExist:
            self.log.warn((f'Zone already exist'))

        self.sort_points = await self.nav.order_zone_points(zone_name, True)
        self.log.info(f'sort points: {self.sort_points}')
        self.sorted_point = await self.nav.get_sorted_zone_point(POS_UNIT.PIXEL)
        self.log.info(f'sorted point: {self.sorted_point}')
        await self.nav.navigate_to_position( 
                x=self.sorted_point['x'], y=self.sorted_point['y'], 
                angle=0.0, pos_unit = POS_UNIT.PIXEL, 
                ang_unit = ANG_UNIT.DEG,
                callback_feedback = self.cb_nav_feedback,
                callback_finish = self.cb_nav_finish,
                wait=False,
            )
        await self.nav.wait_navigation_finished()
        if await self.nav.delete_zone(map_name='unity_apartment',
                                location_name=zone_name):
            self.log.info(f'zone {zone_name} deleted successfully')
        else:
            self.log.info(f'unable to delete zone {zone_name}')
        self.finish_app()


    def cb_nav_finish(self, error, error_msg):
        print(f'cb_nav_finish {error} {error_msg}')


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
        parser.add_argument('-z', '--zone-name',
                            type=str,
                            default='test_zone01', required=False,
                            help='Zone name')

        args = parser.parse_args()

        self.map_name = args.map_name
        self.zone_name = args.zone_name
