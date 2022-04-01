import random

from raya.application_base import RayaApplicationBase

class RayaApplication(RayaApplicationBase):
    async def setup(self):
        self.sound = await self.enable_controller('sound')
        self.sounds = self.sound.get_predefined_sounds()
        self.log.info(f'Available sounds: {self.sounds}')

    async def loop(self):
        sound = random.choice(self.sounds)
        self.log.info(f'Playing random sound: {sound}')
        await self.sound.play_predefined_sound(sound)
        self.finish_app()

    async def finish(self):
        self.log.info(f'Hello from finish()')
