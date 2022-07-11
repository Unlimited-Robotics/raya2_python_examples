import cv2
import math
import sys
from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import POS_UNIT, ANG_UNIT
from raya.exceptions import RayaNavNotNavigating


MAP = 'ur_office_01'


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.counter = 0
        self.nav = await self.enable_controller('navigation')
        self.motion = await self.enable_controller('motion')
        self.list_of_maps = await self.nav.get_list_of_maps()

        self.log.info(f'List of maps: {self.list_of_maps}')
        self.log.info(f'Setting map: {MAP}')

        await self.nav.set_map(MAP, wait_localization=False)

        if not await self.nav.is_localized():
            self.log.info('Waiting for the robot to get localized')
            await self.motion.set_velocity(x=0.0, y=0.0, w=15.0, duration=20.0, 
                                                                    wait=False)

            while (not await self.nav.is_localized()) and self.motion.is_moving():
                await self.sleep(0.1)

            if self.motion.is_moving():
                self.motion.cancel_motion()

            if not await self.nav.is_localized():
                self.log.info((f'Robot couldn\'t localize itself'))
                self.finish_app()
                return
            else:
                self.log.info((f'Robot localized'))
        else:
            self.log.info((f'Robot already localized'))

    
    def cb_nav_finish(self, error, error_msg):
        print(f'cb_nav_finish {error} {error_msg}')


    def cb_nav_feedback(self, state, distance_to_goal, speed):
        print(f'cb_nav_feedback {state} {distance_to_goal} {speed}')


    async def loop(self):

        ### 1 ###
        # await self.sleep(0.2)
        # pos = await self.nav.get_position()
        # self.log.info(f'Robot position: {pos}')
        # self.counter += 1
        # if self.counter >= 25:
        #     self.finish_app()

        ### 2 ###
        await self.nav.navigate_to_position( 
                x=0.0, y=0.0, angle=0.0, pos_unit = POS_UNIT.METERS, 
                # x=383, y=487, angle=90.0, pos_unit = POS_UNIT.PIXEL, 
                ang_unit = ANG_UNIT.DEG,
                callback_feedback = self.cb_nav_feedback,
                callback_finish = self.cb_nav_finish,
                # wait=False,
                wait=True,
            )
        self.log.info('waiting')
        await self.sleep(2.0)
        # await self.nav.cancel_navigation()
        # while self.nav.is_navigating():
            # await self.sleep(0.1)
        # await self.nav.wait_navigation_finished()
        self.log.info('finished')
        await self.sleep(2.0)
        pos = await self.nav.get_position()
        self.log.info(f'Robot position: {pos}')
        self.finish_app()


    async def finish(self):
        try:
            await self.nav.cancel_navigation()
        except RayaNavNotNavigating:
            pass
        self.log.info('Finish app called')
