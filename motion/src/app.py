import argparse

from raya.controllers.motion_controller import MotionController
from raya.application_base import RayaApplicationBase
from raya.enumerations import ANG_UNIT

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        if not self.get_args():
            self.finish_app()
            return
        self.motion_flag = False
        self.motion:MotionController = await self.enable_controller('motion')
        self.nav = await self.enable_controller('navigation')
        self.log.info((f'Setting map: {self.map_name}. '
                       'Waiting for the robot to get localized'))
        if not await self.nav.set_map(self.map_name, 
                                      wait_localization=True, 
                                      timeout=3.0):
            self.log.info(f'Robot couldn\'t localize itself')
            self.finish_app()
        else:
            self.log.info(f'Robot localized')
            self.log.info(f'')


    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-m', '--map-name',
                            type=str, required=True,
                            help='Map name')
        try:
            args = parser.parse_args()
        except:
            return False
        self.map_name = args.map_name
        return True

    
    def cb_motion_finished(self):
        self.log.info('Motion finished callback called!')
        self.motion_flag = False


    async def loop(self):

        self.log.info('Rotating 90 degrees left at 20 deg/sec')
        await self.motion.rotate(angle=90.0, angular_velocity=20.0, 
                                 ang_unit=ANG_UNIT.DEG,
                                 wait=True)
        self.log.info('Motion command finished'); self.log.info('')

        self.log.info('Rotating 1.5708 radians left (90 degrees) at 0.349 rads/sec')
        self.motion_flag = True
        await self.motion.rotate(angle=-1.5708, angular_velocity=0.349, 
                                 ang_unit=ANG_UNIT.RAD,
                                 callback=self.cb_motion_finished)
        while self.motion_flag: await self.sleep(0.1)
        self.log.info('Motion command finished'); self.log.info('')

        self.log.info('Moving forward 0.5 meters at 0.2 m/s')
        await self.motion.move_linear(distance=0.5, x_velocity=0.2, wait=True)
        self.log.info('Motion command finished'); self.log.info('')

        self.log.info('Moving backward 0.5 meters at 0.3 m/s')
        await self.motion.move_linear(distance=-0.5, x_velocity=0.3)
        while self.motion.is_moving(): await self.sleep(0.1)
        self.log.info('Motion command finished'); self.log.info('')

        self.log.info('Moving forward at 0.3 m/s for 2.0 seconds')
        await self.motion.set_velocity(x_velocity=0.3, y_velocity=0.0, 
                                       angular_velocity=0.0, duration=2.0)
        await self.motion.await_until_stop()
        self.log.info('Motion command finished'); self.log.info('')

        self.log.info('Moving backward at 0.3 m/s and rotate at 10 deg/sec')
        self.log.info('for 20 seconds')
        await self.motion.set_velocity(x_velocity=-0.3, y_velocity=0.0, 
                                       angular_velocity=10.0, duration=2.0,
                                       ang_unit=ANG_UNIT.DEG)
        await self.sleep(2.0)
        self.log.info('Canceling motion after 2.0 seconds')
        await self.motion.cancel_motion()
        self.log.info('Motion command finished'); self.log.info('')
        
        self.finish_app()


    async def finish(self):
        try:
            if self.motion.is_moving():
                self.log.info('Stopping motion')
                await self.motion.cancel_motion()
        except AttributeError:
            pass
        self.log.info('Finish app called')
