import matplotlib.pyplot as plt
import numpy as np
import argparse

from raya.application_base import RayaApplicationBase
from raya.controllers.lidar_controller import LidarController
from raya.controllers.lidar_controller import ANG_UNIT


LOOP_PERIOD = 0.1


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.get_args()

        self.obstacle_counter = 0
        self.lidar:LidarController = await self.enable_controller('lidar')
        self.lidar_info = self.lidar.get_laser_info(ang_unit = ANG_UNIT.RAD)
        self.log.info('Laser info:')
        self.log.info(self.lidar_info)

        fig = plt.figure()
        self.ax1 = fig.add_subplot(111, projection='polar')
        
        if self.spin_ena:
            self.motion = await self.enable_controller('motion')
            await self.motion.set_velocity(x_velocity=0.0, y_velocity=0.0, 
                                           angular_velocity=20.0, 
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
        # Get data
        raw_data = self.lidar.get_raw_data()
        theta = np.linspace(self.lidar_info['angle_min'], 
                            self.lidar_info['angle_max'], 
                            len(raw_data))
        # Plot
        self.ax1.clear()
        self.ax1.scatter(x=-np.array(theta)-1.578, y=raw_data, s=2)
        self.ax1.set_ylim(0.0, 10.0)
        plt.pause(0.001) # Needed for real time plotting
        # Check obstacle
        if self.lidar.check_obstacle(lower_angle=0, upper_angle=45,
                                     upper_distance=2.0, ang_unit=ANG_UNIT.DEG):
            self.obstacle_counter += 1
            self.log.info(f'Obstacle {self.obstacle_counter}')
        # Wait
        await self.sleep(LOOP_PERIOD)
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
        self.log.info('App finished')
