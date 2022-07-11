import argparse
from raya.application_base import RayaApplicationBase
from raya.exceptions import RayaGraspingNotGrasping


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        if not self.get_args():
            self.finish_app()
            return
        self.gsp = await self.enable_controller('grasping')        


        await self.gsp.pick_object(detector_model = self.model, 
                source = self.camera, object_name = self.object, 
                arms = self.arms,
                callback_feedback = self.cb_grasping_feedback,
                callback_finish = self.cb_grasping_finish,
                wait=False,
            )

        self.log.info(f'Pick Object started...')
    

    def cb_grasping_finish(self, error, error_msg, result):
        self.finish_app()
        if error != 0:
            self.log.info(f'error: {error} {error_msg}')

        self.log.info(f"Object height: {str(result['height_object'])}")
        self.log.info(f"Arm: {str(result['arm_pick'])}")
        self.log.info('Finish picking object')


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
        except (RayaGraspingNotGrasping, AttributeError):
            pass
        self.log.info('Finish app called')


    def get_args(self):
        parser = argparse.ArgumentParser(description='Pick object example',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("-m", "--model", help="object model name")
        parser.add_argument('-c', '--camera-name', type=str, required=True, 
                            help='name of camera to use')
        parser.add_argument("-o", "--object-name",type=str, default='bottle', help="object to pick")
        parser.add_argument("-a", "--arms",type=str, default=[] ,nargs='+', help="list of arms to try to pick")
        parser.add_argument('-s', '--simulation', dest='simulation', action='store_true')
        try:
            args = parser.parse_args()
        except:
            return False
        self.model = args.model
        self.camera = args.camera_name
        self.object = args.object_name
        self.arms = args.arms
        self.sim = args.simulation
        # If Simulation
        if self.model == None:
            if self.sim:
                self.model = 'coral_efficientdet_lite0_320_coco'
            else:
                self.model = 'gpu_yolov5s_coco'
        return True
