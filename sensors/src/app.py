import json
from raya.application_base import RayaApplicationBase

class RayaApplication(RayaApplicationBase):
    async def setup(self):
        self.i = 0
        # self.motion = await self.enable_controller('motion')
        self.sensors = await self.enable_controller('sensors')
        # await self.motion.set_velocity(x=0.0, y=0.0, w=-0.5, duration=10.0)

    async def loop(self):
        sensors_data = self.sensors.get_all_sensors_values()
        self.log.info('------------------------------')
        self.log.info(f'count: {self.i}')
        self.log.info(json.dumps(sensors_data, indent=2))
        await self.sleep(0.5)
        self.i += 1
        if self.i>100:
            self.finish_app()
        
    async def finish(self):
        # await self.motion.cancel_motion()
        pass
