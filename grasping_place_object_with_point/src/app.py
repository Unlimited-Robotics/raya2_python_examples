import argparse
from raya.application_base import RayaApplicationBase
from raya.exceptions import RayaGraspingNotGrasping


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.get_args()
        self.gsp = await self.enable_controller('grasping')        

        await self.gsp.place_object_with_point(point_to_place = self.point, 
                height_object = self.height_object, arm = self.arm,
                callback_feedback = self.cb_grasping_feedback,
                callback_finish = self.cb_grasping_finish,
                wait=False,
            )

        self.log.info(f'Place Object with point started...')
    

    def cb_grasping_finish(self, error, error_msg):
        self.finish_app()
        if error != 0:
            self.log.info(f'error: {error} {error_msg}')
        self.log.info('Finish place object')


    def cb_grasping_feedback(self, state):
        self.log.info(f'State:  {state}')


    async def loop(self):
        # if await self.nav.is_in_zone(zone_name=self.goal_zone):
        #     self.log.warn(f'Robot in zone')
        #     self.finish_app()
        # else:
        #     self.log.info((f'Robot not in zone'))
        pass

    async def finish(self):
        try:
            await self.gsp.cancel_grasping()
        except RayaGraspingNotGrasping:
            pass
        self.log.info('Finish app called')


    def get_args(self):
        parser = argparse.ArgumentParser(description='Place object with point example',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("-p", "--point-to-place",type=float,default=[0.0, 0.0, 0.0],nargs='+', help="list of floats with the point")
        parser.add_argument("-he", "--height-object",type=float, default='0.14', help="Height of object to place")
        parser.add_argument('-a', '--arm', type=str, required=True, 
                            help='arm to place')
        args = parser.parse_args()
        self.point = args.point_to_place
        self.height_object = args.height_object
        self.arm = args.arm
        print(self.point)