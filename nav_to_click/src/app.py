import argparse
from nis import cat
from re import L
import cv2
import math
import sys
from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import POS_UNIT, ANG_UNIT
from raya.exceptions import RayaNavNotNavigating, RayaNavInvalidGoal
import matplotlib.pyplot as plt


def angle_between_points(p1, p2):
    return math.atan2(p2[1]-p1[1], p2[0]-p1[0])


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.flag = False
        if not self.get_args():
            self.finish_app()
            return
        self.counter = 0
        self.nav = await self.enable_controller('navigation')
        self.list_of_maps = await self.nav.get_list_of_maps()
        self.log.info(f'List of maps: {self.list_of_maps}')
        self.log.info((f'Setting map: {self.map_name}. '
                       'Waiting for the robot to get localized'))
        if not await self.nav.set_map(self.map_name, 
                                      wait_localization=True, 
                                      timeout=3.0):
            self.log.info((f'Robot couldn\'t localize itself'))
            self.finish_app()
            return
        self.log.info(f'Using map \'{self.map_name}\'')
        self.map_image, self.map_info = await self.nav.get_map(
                                                    self.map_name)
        
        cv2.namedWindow('map')
        cv2.setMouseCallback('map',self.get_click_coordinates)
        self.click_down = False
        self.point_down = (0,0)
        self.point_mouse = (0,0)
        self.new_goal = (0,0,0)
        self.new_flag = False

        self.log.info('')
        self.log.info('Controls:')
        self.log.info('  - ESC: Exit')
        self.log.info('  - Click and hold: set position and orientation')
        self.log.info('  - C: Cancel current navigation')

    
    def cb_nav_finish(self, error, error_msg):
        print(f'cb_nav_finish {error} {error_msg}')


    def cb_nav_feedback(self, state, distance_to_goal, speed):
        print(f'cb_nav_feedback {state} {distance_to_goal} {speed}')


    async def loop(self):
        robot_position = await self.nav.get_position(
                    pos_unit = POS_UNIT.PIXEL, ang_unit = ANG_UNIT.RAD)
        img = self.draw(robot_position)
        cv2.imshow("map", img)
        key = cv2.waitKey(20) & 0xFF
        if key == 27:
            self.finish_app()
        if key == ord('C') or key == ord('c'):
            if self.nav.is_navigating():
                self.log.info('Cancelling current navigation')
                try:
                    await self.nav.cancel_navigation()
                except:
                    self.log.error('No navigation in execution...')
        if self.new_flag:
            if self.nav.is_navigating():
                self.log.warn('Cancel current goal before send a new one.')
                self.new_flag = False
            else:
                self.log.warn(f'New goal received {self.new_goal}')
                try:
                    await self.nav.navigate_to_position( 
                        # x=0.0, y=1.0, angle=90.0, pos_unit = POS_UNIT.METERS, 
                        x=self.new_goal[0], y=self.new_goal[1], 
                        angle=self.new_goal[2], pos_unit = POS_UNIT.PIXEL, 
                        ang_unit = ANG_UNIT.RAD,
                        callback_feedback = self.cb_nav_feedback,
                        callback_finish = self.cb_nav_finish,
                        # wait=False,
                        wait=False,
                    )
                except RayaNavInvalidGoal:
                    self.log.warn(f'Invalid goal')
                self.new_flag = False



    async def finish(self):
        try:
            await self.nav.cancel_navigation()
        except (RayaNavNotNavigating, AttributeError):
            pass
        self.log.info('Finish app called')


    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-m', '--map-name',
                            type=str,
                            default='', required=True,
                            help='Map name')
        try:
            args = parser.parse_args()
        except:
            return False
        self.map_name = args.map_name
        return True

    
    def draw(self, robot_position):
        img = self.map_image.copy()
        x_pixel  = robot_position["x"]
        y_pixel  = robot_position["y"]
        rotation = robot_position["angle"]
        x_line   =  x_pixel + int(7 * math.cos(-rotation))
        y_line   =  y_pixel + int(7 * math.sin(-rotation))
        cv2.circle(img, (x_pixel, y_pixel), 8, (255,0,0), 2)      
        cv2.line(img, (x_pixel, y_pixel), (x_line, y_line), (0,0,255), 4)
        if self.click_down:
            cv2.arrowedLine(img, self.point_down, self.point_mouse, (0,150,0), 3)
        return img


    def get_click_coordinates(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.point_down = (x, y)
            self.point_mouse = (x, y)
            self.click_down = True
        elif event == cv2.EVENT_LBUTTONUP:
            self.new_goal = (
                    self.point_down[0],
                    self.point_down[1],
                    -angle_between_points(self.point_down, self.point_mouse)
                )
            self.new_flag = True
            self.click_down = False
        elif event == cv2.EVENT_MOUSEMOVE:
            self.point_mouse = (x, y)

