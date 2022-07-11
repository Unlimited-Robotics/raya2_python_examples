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
            await self.execute_gripper()

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
        parser.add_argument('-o', '--open',
                            type=bool, required=False,
                            help='true for open the gripper for default is false',
                            default=False)
        parser.add_argument('-w', '--width',
                            type=float, required=False,
                            help='if you want to close define how much space should be between finger of gripper ')
        parser.add_argument('-p', '--pressure',
                            type=float, required=False,
                            help='if you want to close define how much pressure should the gripper exert')

        try:
            args = parser.parse_args()
            self.arm_name = args.arm_name
            self.list_arms = args.list_arms
            self.open = args.open
            self.pressure = args.pressure
            self.width = args.width
        except:
            self.list_arms = True

        print(self.open)

    def print_list_arms(self):
        print("\n---------------------")
        print(f"{self.col.OKBLUE}List of avaliable arms{self.col.ENDC}")
        for c, arm_name in enumerate(self.arms.get_list_of_arms()):
            print(f"{c}. {arm_name}")

    def check_values(self):
        if not self.open:
            if self.width is None and self.pressure:
                raise ValueError("if you are going to close must define width and presure")
            if not self.width:
                raise ValueError("width must be positive")

    async def execute_gripper(self):
        action = "Oppening" if self.open else "Clossing"
        print(f"\n{action} the gripper of the arm {self.arm_name}")

        if self.open:
            await self.arms.set_gripper_open(self.arm_name,
                                             callback_finish=self.callback_finish,
                                             wait=True)
        else:
            await self.arms.set_gripper_close(self.arm_name,
                                              desired_pressure=self.pressure,
                                              width=self.width,
                                              callback_finish=self.callback_finish,
                                              wait=True)

    def callback_finish(self, error, error_msg, hand, action: str):
        if error == 0:
            print(f"\n{self.col.OKGREEN}FINISH SUCCESSFULLY THE EXECUTION OF THE {action.upper()}")
        else:
            print(f"\n{self.col.FAIL}ERROR {error} IN THE EXECUTION: {error_msg}{self.col.ENDC}")
        print("------------")
        print("")
