import random

from raya.application_base import RayaApplicationBase

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info(f'Hello from setup()')
        
        self.leds = await self.enable_controller('leds')
        self.leds_groups = self.leds.get_groups()

        self.log.info('LEDS GROUPS:')
        self.log.info(self.leds_groups)
        self.log.info('')
        await self.sleep(2.0)


    async def loop(self):

        for group in self.leds_groups:
            self.log.info(f'GROUP: {group}')
            self.log.info(f'')
            colors = self.leds.get_colors(group)
            self.log.info(f'- COLORS: {colors}')
            animations = self.leds.get_animations(group)
            self.log.info(f'- ANIMATIONS: {animations}')
            max_speed = self.leds.get_max_speed(group)
            self.log.info(f'- MAX SPEED: {max_speed}')
            color = random.choice(colors)
            animation = random.choice(animations)
            speed = random.randint(1, max_speed)
            repetitions = random.randint(1,3)
            self.log.info(f'')
            self.log.info(f'Running: group={group}, animation={animation}')
            self.log.info(f'         speed={speed}, repetitions={repetitions}')
            await self.leds.animation(group, color, animation, speed, 
                                                                repetitions)
            self.log.info(f'')
            self.log.info(f'')
            await self.sleep(2.0)

        await self.sleep(3.0)

        self.finish_app()


    async def finish(self):

        self.log.info(f'Hello from finish()')