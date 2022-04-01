import random

from raya.application_base import RayaApplicationBase
from raya.logger import create_logger as LogLevel

class RayaApplication(RayaApplicationBase):
    async def setup(self):
        self.interactions = await self.enable_controller('interactions')
        self.interactions_list = self.interactions.get_predefeined_interactions()
        self.log.info(f'Available interactions: {self.interactions_list}')

    async def loop(self):
        interaction = random.choice(self.interactions_list)
        self.log.info(f'Playing random interaction: {interaction}')
        await self.interactions.play_predefined_interaction(interaction, wait=True)
        self.log.info('Interaction finished')
        self.finish_app()

    async def finish(self):
        pass
