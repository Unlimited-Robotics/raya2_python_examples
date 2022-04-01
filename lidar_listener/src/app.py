from raya.application_base import RayaApplicationBase
from raya.controllers.lidar_controller import LidarController
from raya.controllers.lidar_controller import ANG_UNIT

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.i = 0
        self.motion = await self.enable_controller('motion')
        self.lidar: LidarController = await self.enable_controller('lidar')
        self.lidar.create_obstacle_listener(listener_name='obstacle',
                                              callback=self.callback_obstacle,
                                              lower_angle=260,
                                              upper_angle=280,
                                              upper_distance=2.0, 
                                              ang_unit=ANG_UNIT.DEG)
        await self.motion.set_velocity(x=0.0, y=0.0, w=-0.5, duration=100.0)


    async def loop(self):
        await self.sleep(1.0)
        self.log.info('Doing other (non blocking) stuff!')


    async def finish(self):
        await self.motion.cancel_motion()
        self.lidar.delete_listener(listener_name='obstacle')


    def callback_obstacle(self):
        self.log.warning('Obstacle!')
