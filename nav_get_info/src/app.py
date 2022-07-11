import sys
import argparse
from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import POS_UNIT, ANG_UNIT
from raya.exceptions import RayaNavZonesNotFound

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.get_args()
        self.nav = await self.enable_controller('navigation')
        if not await self.nav.set_map(self.map_name, 
                                      wait_localization=True, 
                                      timeout=3.0):
            self.log.info((f'Robot couldn\'t localize itself'))
            self.finish_app()
        self.list_of_maps = await self.nav.get_list_of_maps()
        self.status = await self.nav.get_status()
        self.log.info(f'status: {self.status}')

        self.zones = await self.nav.get_zones(self.map_name)
        self.log.info(f'zones: {self.zones}')

        self.locations = await self.nav.get_locations(self.map_name)
        self.log.info(f'locations: {self.locations}')

        self.zones_list = await self.nav.get_zones_list(self.map_name)
        self.log.info(f'zones_list: {self.zones_list}')

        self.locations_list = await self.nav.get_locations_list(self.map_name)
        self.log.info(f'locations_list: {self.locations_list}')

        self.location = await self.nav.get_location('kitchen', POS_UNIT.PIXEL)
        self.log.info(f'kitchen: {self.location}')

        self.zone_center = await self.nav.get_zone_center('kitchen', POS_UNIT.PIXEL)
        self.log.info(f'kitchen center: {self.zone_center}')
        
        self.sort_points = await self.nav.order_zone_points('kitchen', True)
        self.sorted_point = await self.nav.get_sorted_zone_point(POS_UNIT.PIXEL)
        self.log.info(f'kitchen first point: {self.zone_center}')

        try:
            if await self.nav.delete_zone(map_name=self.map_name,
                                    location_name='test001'):
                print(f'zone test001 deleted successfully')
        except RayaNavZonesNotFound:
            self.log.info((f'Location not found'))
        try:
            if await self.nav.delete_location(map_name=self.map_name,
                                    location_name= 'test001'):
                print(f'location test001 deleted successfully')
        except RayaNavZonesNotFound:
            self.log.info((f'Location not found'))
        if not await self.nav.save_location( 
                location_name='test001', x=1.0, y=0.5, angle=1.0, 
                pos_unit = POS_UNIT.METERS, ang_unit = ANG_UNIT.RAD
                ):
            self.log.info((f'Unable to save location'))
            self.finish_app()
        self.log.info((f'Location saved successfully'))
        if not await self.nav.save_zone( 
                zone_name='test001', 
                points=[[0, 1],[1, 1],[1, 0],[0, 0]], 
                pos_unit = POS_UNIT.METERS
                ):
            self.log.info((f'Unable to save zone'))
            self.finish_app()

        self.log.info((f'Zone saved succesfully'))
        self.finish_app()


    async def loop(self):
        pass


    async def finish(self):
        self.log.info('Finish app called')


    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-m', '--map-name',
                            type=str,
                            default='', required=True,
                            help='Map name')

        args = parser.parse_args()

        self.map_name = args.map_name
        
        
