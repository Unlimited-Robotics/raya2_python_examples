import argparse
from raya.application_base import RayaApplicationBase
import json

from raya.enumerations import ANG_UNIT


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.get_args()
        self.col = bcolors()
        # enable the arm controller
        self.arms = await self.enable_controller("arms")
        if self.list_arms:
            self.print_list_arms()

        elif self.arm_name:
            if not self.arm_name in self.arms.get_list_of_arms():
                self.print_list_arms()
                raise ValueError(f"the arm name {self.arm_name} is invalid")
            self.check_values()
            await self.execute_pose()

    async def loop(self):
        self.finish_app()

    async def finish(self):
        print(f"{self.col.OKGREEN}\nApplication has finished{self.col.ENDC}")

    def get_args(self):
        parser = argparse.ArgumentParser(
            description='Allows to the user check if set a specific pose is valid')
        parser.add_argument('-a', '--arm-name',
                            type=str, required=False,
                            help='the name of the arm that you want to validate a position',
                            default="left_arm")
        parser.add_argument('-l', '--list-arms',
                            type=bool, required=False,
                            help='use this option if you want to list the avaliable arms, when this \
option is true the program just print the list of avaliable arms')
        parser.add_argument('-p', '--pose',
                            type=str, required=False,
                            help='Define the pose that you want to check, the format should be a \
json like this {"x":0.38661,"y":0.25621,"z":1.18,"r":0,"p":-90,"yaw":0} where xyz are the position\
and rp,yaw are the orientation value in euler angles representation',
                            default='{"x":0.38661,"y":0.25621,"z":1.18,"r":0,"p":-90,"yaw":0}')
        parser.add_argument('-r', '--rad-deg',
                            type=bool, required=False,
                            help='use this option if you want to pass the values of the joints in rad')

        try:
            args = parser.parse_args()
            self.arm_name = args.arm_name
            self.list_arms = args.list_arms
            self.pose = json.loads(args.pose)
            self.rad_deg = args.rad_deg
        except:
            self.list_arms = True

    def print_list_arms(self):
        print("\n---------------------")
        print(f"{self.col.OKBLUE}List of avaliable arms{self.col.ENDC}")
        for c, arm_name in enumerate(self.arms.get_list_of_arms()):
            print(f"{c}. {arm_name}")

    def check_values(self):
        keys = ["x", "y", "z", "r", "p", "yaw"]
        for k in self.pose.keys():
            if not k in keys:
                raise ValueError(f"invalid key of the json {k}")

        for k in keys:
            if not k in self.pose.keys():
                raise ValueError(f"the key {k} of the json is missing")

    async def execute_pose(self):
        print(f"\nPose to execute for the arm {self.arm_name}")
        print("key\tvalue")
        for key in self.pose:
            print(f"{key}\t{self.pose[key]}")
        units = ANG_UNIT.DEG
        if self.rad_deg:
            units = ANG_UNIT.RAD

        await self.arms.set_pose(
            self.arm_name,
            x=self.pose["x"],
            y=self.pose["y"],
            z=self.pose["z"],
            roll=self.pose["r"],
            pitch=self.pose["p"],
            yaw=self.pose["yaw"],
            units=units,
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            wait=True,
        )

    def callback_feedback(self, arg1, arg2):
        print(f"ARM:{arg1} PERCENTAGE:{arg2:.2f}")

    def callback_finish(self, error, error_msg):
        if error == 0:
            print(f"\n{self.col.OKGREEN}FINISH SUCCESSFULLY THE EXECUTION OF THE POSE")
        else:
            print(f"\n{self.col.FAIL}ERROR IN THE EXECUTION NUMBER: {error}{self.col.ENDC}")
        print("------------")
        print("")
