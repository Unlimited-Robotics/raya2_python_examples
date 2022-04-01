from raya.application_base import RayaApplicationBase

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.i = 0


    async def loop(self):
        self.log.info('Loop')
        await self.sleep(0.5)
        self.i += 1
        if self.i==300:
            self.finish_app()


    async def finish(self):
        self.log.info('App finished')

