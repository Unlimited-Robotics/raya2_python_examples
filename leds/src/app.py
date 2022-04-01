from raya.application_base import RayaApplicationBase
from raya.logger import create_logger

class RayaApplication(RayaApplicationBase):
    async def setup(self):
        self.leds = await self.enable_controller('leds')
        self.log.info(f'Hello from setup()')

    async def loop(self):

        print('LEDS GROUPS:')
        print(self.leds.get_groups())

        print('\nCHEST:')
        print(self.leds.get_colors('chest'))
        print(self.leds.get_animations('chest'))
        print(self.leds.get_max_speed('chest'))
        await self.leds.animation('chest', 'red_basic', 'motion_1', 10, 9)

        print('\nHEAD:')
        print(self.leds.get_colors('head'))
        print(self.leds.get_animations('head'))
        print(self.leds.get_max_speed('head'))
        await self.leds.animation('head', 'blue_basic', 'motion_1', 10, 9)

        print('\nSKIRT:')
        print(self.leds.get_colors('skirt'))
        print(self.leds.get_animations('skirt'))
        print(self.leds.get_max_speed('skirt'))
        await self.leds.animation('skirt', 'green_basic', '0000', 10, 0)

        print('\SENSORS:')
        print(self.leds.get_colors('sensors'))
        print(self.leds.get_animations('sensors'))
        print(self.leds.get_max_speed('sensors'))
        await self.leds.animation('sensors', 'white', '000', 10, 0)

        self.finish_app()

    async def finish(self):

        self.log.info(f'Hello from finish()')