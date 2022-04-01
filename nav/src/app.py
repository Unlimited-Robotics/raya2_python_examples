import cv2
import math
import sys
from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import POS_UNIT, ANG_UNIT
from raya.exceptions import RayaNavAlreadyNavigating


def angle_between_points(p1, p2):
    return math.atan2(p2[1]-p1[1], p2[0]-p1[0])


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.flag = False
        self.navigation = await self.enable_controller('navigation')
        self.maps_list = await self.navigation.get_list_of_maps()
        if not self.maps_list:
            self.log.error('Not maps available')
            self.finish_app()
            return
        self.log.info(f'Available maps: {self.maps_list}')
        #self.map_name = 'test_mapOffice01'
        if len(sys.argv)==1:
            self.log.error('Map name must be provided as argument')
            exit(1)
        self.map_name = sys.argv[1]
        self.map_image, self.map_info = await self.navigation.get_map(self.map_name)
        try:
            self.log.info(f'Wait, starting navigation...')
            await self.navigation.enable_navigation(self.map_name)
        except:
            self.log.error(f'Error starting navigation.')
        self.log.info(f'Using map \'{self.map_name}\'')

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


    async def loop(self):
        robot_position = self.navigation.get_position(pos_unit = POS_UNIT.PIXEL, ang_unit = ANG_UNIT.RAD)
        img = self.draw(robot_position)
        cv2.imshow("map", img)
        key = cv2.waitKey(20) & 0xFF
        if key == 27:
            self.finish_app()
        if key == ord('C') or key == ord('c'):
            if self.navigation.is_navigating():
                self.log.info('Cancelling current navigation')
                try:
                    await self.navigation.cancel_navigation()
                except:
                    self.log.error('No navigation in execution...')
        if self.new_flag:
            print(self.new_goal)
            try:
                await self.navigation.navigate_to_position( x=self.new_goal[0], 
                                                            y=self.new_goal[1], 
                                                            angle=self.new_goal[2],
                                                            pos_unit = POS_UNIT.PIXEL, 
                                                            ang_unit = ANG_UNIT.RAD
                                                        )
            except:
                self.log.error('Cancel current navigation before request a new one...')
            self.new_flag = False


    async def finish(self):
        self.log.info('Finish app called')
        await self.sleep(0.5)
        #TODO: Check is_navigating flag with multiple goals
        try:
            self.log.info('disable navigation')
            await self.sleep(0.5)
            await self.navigation.disable_navigation()
        except:
            self.log.info('disable navigation error')
        try:
            self.log.info('Cancelling current navigation')
            await self.navigation.cancel_navigation()
        except:
            self.log.info('Cancelling current navigation error')
        
    
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

