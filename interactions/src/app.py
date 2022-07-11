import random

from raya.application_base import RayaApplicationBase
from raya.controllers.interactions_controller import InteractionsController

class RayaApplication(RayaApplicationBase):
    async def setup(self):
        self.interactions:InteractionsController = await self.enable_controller('interactions')
        self.interactions_list = self.interactions.get_predefeined_interactions()
        self.log.info(f'Available interactions: {self.interactions_list}')

    async def loop(self):
        interaction = random.choice(self.interactions_list)
        self.log.info(f'Playing random interaction: {interaction}')
        await self.interactions.play_predefined_interaction(interaction, wait=True)
        self.log.info('Interaction finished')

        await self.sleep(1.0)
        
        interaction = random.choice(self.interactions_list)
        self.log.info(f'Playing random interaction: {interaction}')
        await self.interactions.play_predefined_interaction(interaction, wait=False)
        await self.interactions.wait_interaction_finished()
        self.log.info('Interaction finished')

        await self.sleep(1.0)
        
        interaction = random.choice(self.interactions_list)
        self.log.info(f'Playing random interaction: {interaction}')
        await self.interactions.play_predefined_interaction(interaction, wait=False)
        while self.interactions.interaction_running():
            await self.sleep(0.1)
        self.log.info('Interaction finished')

        self.finish_app()

    async def finish(self):
        pass
