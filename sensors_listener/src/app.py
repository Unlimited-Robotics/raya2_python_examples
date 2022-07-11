from raya.application_base import RayaApplicationBase

class RayaApplication(RayaApplicationBase):
    async def setup(self):
        self.i = 0
        self.sensors = await self.enable_controller('sensors')
        self.sensors.create_threshold_listener(listener_name='thermometer',
                                               callback = self.callback_thermometer,
                                               sensors_paths = ['/environment/temperature'],
                                               lower_bound = 28.0)

    async def loop(self):
        await self.sleep(1.0)
        self.log.info('Doing other (non blocking) stuff...')
        
    async def finish(self):
        self.sensors.delete_listener(listener_name='thermometer')

    def callback_thermometer(self):
        self.log.warning('Environment temperature over 28 degrees!')
