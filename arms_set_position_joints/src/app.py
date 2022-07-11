import argparse

import numpy as np
from raya.application_base import RayaApplicationBase


from raya.enumerations import ANG_UNIT


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"

    def disable(self):
        self.HEADER = ""
        self.OKBLUE = ""
        self.OKGREEN = ""
        self.WARNING = ""
        self.FAIL = ""
        self.ENDC = ""


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
            if self.joint_values is not None:
                self.check_values()
                await self.execute_position_joints(
                    self.joint_values, self.arms.get_state_of_arm(self.arm_name)["name"]
                )
            else:
                print(
                    f"\n{self.col.FAIL}DEFINE THE JOINTS VALUES ARRAY TO EXECUTE(-j){self.col.ENDC}"
                )
                self.list_joints_values()

    async def loop(self):
        self.finish_app()

    async def finish(self):
        print(f"{self.col.OKGREEN}\nApplication has finished{self.col.ENDC}")

    def get_args(self):
        parser = argparse.ArgumentParser(
            description="Allows to the user check if a specific position joints is valid"
        )
        parser.add_argument(
            "-a",
            "--arm-name",
            type=str,
            required=False,
            help="the name of the arm that you want to validate a position",
            default="left_arm",
        )
        parser.add_argument(
            "-l",
            "--list-arms",
            type=bool,
            required=False,
            help="use this option if you want to list the avaliable arms, when this \
option is true the program just print the list of avaliable arms",
        )
        parser.add_argument(
            "-r",
            "--rad-deg",
            type=bool,
            required=False,
            help="use this option if you want to pass the values of the joints in rad",
        )
        parser.add_argument(
            "-j",
            "--joint-values",
            type=str,
            required=False,
            help="Define the value of the joints in array format 0,0,0,0,0,0,0",
        )
        self.rad_deg = False
        try:
            args = parser.parse_args()
            self.arm_name = args.arm_name
            self.list_arms = args.list_arms
            self.rad_deg = args.rad_deg
            try:
                self.joint_values = np.fromstring(args.joint_values, sep=",").tolist()
            except:
                self.joint_values = None
        except:
            self.list_arms = True

    def print_list_arms(self):
        print("\n---------------------")
        print(f"{self.col.OKBLUE}List of avaliable arms{self.col.ENDC}")
        for c, arm_name in enumerate(self.arms.get_list_of_arms()):
            print(f"{c}. {arm_name}")

    def list_joints_values(self):
        print("\n---------------------")
        print(
            f"{self.col.OKBLUE}List of joints of the arm: {self.arm_name}{self.col.ENDC}"
        )
        print(f"idx name\t\t\tlower limit\tupper_limit")
        units = ANG_UNIT.DEG
        if self.rad_deg:
            units = ANG_UNIT.RAD
        limits = self.arms.get_limits_of_joints(self.arm_name, units)
        name_joints = self.arms.get_state_of_arm(self.arm_name)["name"]
        for c, joint_name in enumerate(name_joints):
            print(
                f"{c}.  {joint_name}\t{limits[joint_name][0]:.2f}\t\t{limits[joint_name][1]:.2f}"
            )

    def check_values(self):
        name_joints = self.arms.get_state_of_arm(self.arm_name)["name"]
        if len(self.joint_values) != len(name_joints):
            raise ValueError(
                f"Invalid length of the joint values array must be {len(name_joints)}"
            )

    async def execute_position_joints(self, joints, names):
        print("\nPosition joints to validate \nname of joint\tvalue")
        for joint, name in zip(joints, names):
            print(f"{name}\t{joint}")
        units = ANG_UNIT.DEG
        if self.rad_deg == True:
            units = ANG_UNIT.RAD
        await self.arms.set_joints_position(
            self.arm_name,
            names,
            joints,
            units=units,
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            wait=True,
        )

    def callback_feedback(self, arg1, arg2):
        print(f"ARM:{arg1} PERCENTAGE:{arg2:.2f}")

    def callback_finish(self, error, error_msg):
        if error == 0:
            print(
                f"\n{self.col.OKGREEN}FINISH SUCCESSFULLY THE EXECUTION OF THE POSITION JOINTS"
            )
        else:
            print(
                f"\n{self.col.FAIL}ERROR IN THE EXECUTION NUMBER: {error}{self.col.ENDC}"
            )
        print("------------")
        print("")
