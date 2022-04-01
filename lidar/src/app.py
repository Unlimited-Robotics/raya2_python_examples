from raya.application_base import RayaApplicationBase
from raya.controllers.lidar_controller import LidarController

import time
import numpy as np
from raya.controllers.lidar_controller import ANG_UNIT

MOTION = True

import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install('matplotlib')

import matplotlib.pyplot as plt

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.i = 0
        self.lidar = await self.enable_controller('lidar')
        fig = plt.figure()
        self.ax1 = fig.add_subplot(111, projection='polar')
        self.lidar_info = self.lidar.get_laser_info(ang_unit = ANG_UNIT.RAD)
        self.log.info('Laser info:')
        self.log.info(self.lidar_info)
        self.i = 0
        if MOTION:
            self.motion = await self.enable_controller('motion')
            await self.motion.set_velocity(x=0.0, y=0.0, w=-0.5, duration=100.0)

    async def loop(self):
        # Get data
        raw_data = self.lidar.get_raw_data()
        theta = np.linspace(self.lidar_info['angle_min'], 
                            self.lidar_info['angle_max'], 
                            len(raw_data))
        # Plot
        self.ax1.clear()
        self.ax1.scatter(x=theta, y=raw_data, s=2)
        self.ax1.set_ylim(0.0, 10.0)
        plt.pause(0.001) # Needed for real time plotting
        # Check obstacle
        if self.lidar.check_obstacle(lower_angle=260, upper_angle=280,
                                     upper_distance=2.0, ang_unit=ANG_UNIT.RAD):
            self.log.info(f'Obstacle {self.i}')
        # Wait
        self.i += 1
        await self.sleep(0.1)
        if self.i>100:
            self.finish_app()
        
    async def finish(self):
        if MOTION:
            await self.motion.cancel_motion()
