from raya.application_base import RayaApplicationBase
import time

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.flag = False
        self.motion = await self.enable_controller('motion')


    async def loop(self):

        await self.sleep(1.0)
        self.log.info('Motion command 1')
        # Move and wait in the same command
        await self.motion.set_velocity(x=0.0, y=0.0, w=-0.5, duration=1.0, wait=True)

        await self.sleep(1.0)
        self.log.info('Motion command 2')
        # Start motion commmand and cancel it before
        await self.motion.set_velocity(x=0.0, y=0.0, w=0.5, duration=5.0)
        await self.sleep(2.0)
        self.log.info('Cancel command')
        await self.motion.cancel_motion()

        await self.sleep(1.0)
        self.log.info('Motion command 3')
        await self.motion.set_velocity(x=0.0, y=0.0, w=-0.5, duration=2.0, callback=self.cb_motion)
        while not self.flag:
            await self.sleep(0.1)

        await self.sleep(1.0)
        self.log.info('Motion command 4')
        await self.motion.set_velocity(x=0.0, y=0.0, w=0.5, duration=3.0)
        await self.motion.await_until_stop()
        
        self.finish_app()


    async def finish(self):
        if self.motion.is_moving():
            self.log.info('Stopping motion')
            await self.motion.cancel_motion()


    def cb_motion(self):
        self.log.info('Stop')
        self.flag = True