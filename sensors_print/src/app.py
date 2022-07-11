import json
from raya.application_base import RayaApplicationBase

class RayaApplication(RayaApplicationBase):
    async def setup(self):
        self.i = 0
        self.sensors = await self.enable_controller('sensors')

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
        pass
