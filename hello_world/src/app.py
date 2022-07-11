from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import NavigationController
from raya.controllers.motion_controller import MotionController
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
from raya.controllers.grasping_controller import GraspingController
from raya.controllers.arms_controller import ArmsController
from raya.controllers.communication_controller import CommunicationController
from raya.controllers.navigation_controller import ANG_UNIT, POS_UNIT
from raya.exceptions import *

CAMERA = 'head_front'
AVAILABLE_OBJECTS = ['cup']
MAP = 'unity_apartment'
MODEL = 'apartment_objects'
ARM_NAME = 'right_arm'

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        #1
        self.motion: MotionController = await self.enable_controller('motion')

        #2
        self.cameras: CamerasController = await self.enable_controller('cameras')
        self.arms: ArmsController = await self.enable_controller('arms')

        self.nav: NavigationController = await self.enable_controller('navigation')
        self.cv: CVController = await self.enable_controller('cv')
        self.grasp: GraspingController = await self.enable_controller('grasping')

        self.comm: CommunicationController = await self.enable_controller('communication')

        self.msg_rcvd = None
        self.comm.create_incoming_msg_listener(callback=self.cb_incoming_msg)

        if not await self.nav.set_map(MAP, wait_localization=True, timeout=3.0):
            self.finish_app()

        
        await self.cameras.enable_color_camera(CAMERA)

        self.current_detections = []
        self.detector = await self.cv.enable_model(model='detectors',type='object',
                                                    name=MODEL,
                                                    source=CAMERA,
                                                    model_params={}
                                                    )

        


    def cb_incoming_msg(self, msg):
        self.msg_rcvd = msg


    async def loop(self):

        ## WAIT FOR MESSAGE
        self.log.info(f'Waiting for an incoming message.')
        while self.msg_rcvd is None:
            await self.sleep(0.2)
        self.log.info(f'Message received.')

        target_object = self.msg_rcvd['selected_option']['name']
        if target_object not in AVAILABLE_OBJECTS:
            self.log.error(f'Object \'{target_object}\' is not available')
            self.finish_app()
            return

        await self.comm.send_msg({"action": "searching"})
        ## LOOK FOR THE OBJECT
        self.log.info(f'Looking for the object \'{target_object}\'')
        await self.motion.rotate(angle=360.0, angular_velocity=10.0, ang_unit=ANG_UNIT.DEG, wait=False)
        resp = await self.detector.find_objects([target_object], wait=True, timeout=40.0)
        if resp and self.motion.is_moving():            
            await self.motion.cancel_motion()
        else:
            self.log.error(f'Object not found, finishing the app')
            self.finish_app()
            return
        obj_x, obj_y = resp[0]['center_point_map'][0:2]
        self.log.info(f'Object found in x:{obj_x} y:{obj_y}')

        await self.comm.send_msg({"action": "navigating"})
        ## NAVIGATE TO THE OBJECT
        await self.sleep(0.5)
        self.log.info(f'Navigating close to the object')
        try:
            await self.nav.navigate_close_to_position(x=obj_x, y=obj_y,
                                                pos_unit=POS_UNIT.METERS,
                                                wait=True)
        except RayaNavInvalidGoal:
            self.log.error('It\'s not possible to get the object location')
            self.finish_app()
            return

        await self.comm.send_msg({"action": "approaching"})
        ## APPROACH TO THE OBJECT
        self.log.info(f'Approaching to the object')
        await self.motion.move_linear(distance=0.05, x_velocity=0.1, wait=True)

        await self.comm.send_msg({"action": "picking"})
        ## PICK THE OBJECT
        self.log.info(f'Picking the object')
        for _ in range(3):
            try:
                await self.sleep(0.5)
                await self.grasp.pick_object(detector_model=MODEL, 
                        source=CAMERA, object_name=target_object,
                        wait=True, arms=['right_arm'])
                break
            except RayaGraspingException:
                continue
        
        await self.comm.send_msg({"action": "done"})
        self.finish_app()

    async def finish(self):
        await self.cv.disable_model(model='detectors',type='object')
        self.cameras.disable_color_camera(CAMERA)
        if self.motion.is_moving():
            await self.motion.cancel_motion()
