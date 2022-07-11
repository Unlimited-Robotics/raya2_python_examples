import argparse
from raya.application_base import RayaApplicationBase
from raya.exceptions import RayaGraspingNotGrasping


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.get_args()
        self.gsp = await self.enable_controller('grasping')        

        await self.gsp.place_object_with_reference(detector_model = self.model, 
                source = self.camera, object_name = self.object, height_object= self.height_object, distance = self.distance,
                arm = self.arm,
                callback_feedback = self.cb_grasping_feedback,
                callback_finish = self.cb_grasping_finish,
                wait=False,
            )

        self.log.info(f'Place Object started...')
    

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
        parser = argparse.ArgumentParser(description='Place object example',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("-m", "--model", help="object model name")
        parser.add_argument('-c', '--camera-name', type=str, required=True, 
                            help='name of camera to use')
        parser.add_argument("-o", "--object-reference",type=str, default='cup', help="object reference to place")
        parser.add_argument("-he", "--height-object",type=float, default='0.14', help="Height of object to place")
        parser.add_argument("-d", "--distance",type=float, default='0.1', help="Distance in meters to put it from reference object")
        parser.add_argument('-a', '--arm', type=str, required=True, 
                            help='arm to place')
        parser.add_argument('-s', '--simulation', dest='simulation', action='store_true')
        args = parser.parse_args()
        self.model = args.model
        self.camera = args.camera_name
        self.object = args.object_reference
        self.sim = args.simulation
        self.height_object = args.height_object
        self.distance = args.distance
        self.arm = args.arm
        # If Simulation
        if self.model == None:
            if self.sim:
                self.model = 'coral_efficientdet_lite0_320_coco'
            else:
                self.model = 'gpu_yolov5s_coco'
