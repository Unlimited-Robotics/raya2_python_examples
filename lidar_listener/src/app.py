import argparse

from raya.application_base import RayaApplicationBase
from raya.controllers.lidar_controller import LidarController
from raya.controllers.lidar_controller import ANG_UNIT


LOOP_PERIOD = 1.0


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.get_args()

        self.lidar:LidarController = await self.enable_controller('lidar')
        self.lidar.create_obstacle_listener(listener_name='obstacle',
                                              callback=self.callback_obstacle,
                                              lower_angle=260,
                                              upper_angle=280,
                                              upper_distance=2.0, 
                                              ang_unit=ANG_UNIT.DEG)

        if self.spin_ena:
            self.motion = await self.enable_controller('motion')
            await self.motion.set_velocity(x_velocity=0.0, y_velocity=0.0, 
                                           angular_velocity=-20.0, 
                                           duration=self.duration)
        else:
            self.time_counter = 0
            self.max_loops = self.duration / LOOP_PERIOD

    
    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--spin', action='store_true', 
                            help='Spins while scanning')
        parser.add_argument('-d', '--duration',
                            type=float, default=10.0,
                            help='Scanning duration')
        parser.set_defaults(feature=True)
        args = parser.parse_args()
        self.spin_ena = args.spin
        self.duration = args.duration


    async def loop(self):
        await self.sleep(LOOP_PERIOD)
        self.log.info('Doing other (non blocking) stuff!')
        if self.spin_ena:
            if not self.motion.is_moving():
                self.finish_app()
        else:
            self.time_counter += 1
            if self.time_counter >= self.max_loops:
                self.finish_app()


    async def finish(self):
        if self.spin_ena and self.motion.is_moving():
            await self.motion.cancel_motion()
        self.lidar.delete_listener(listener_name='obstacle')


    def callback_obstacle(self):
        self.log.warning('Obstacle!')
