import argparse
from cmath import e
from gc import callbacks
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
            if self.predefined_pose:
                self.check_predefined_pose()
                await self.execute_predefined_pose(self.predefined_pose)
            else:
                print(
                    f"\n{self.col.FAIL}DEFINE THE PREDEFINED POSE TO EXECUTE (-p){self.col.ENDC}"
                )
                self.list_predefined_poses()

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
            "-p",
            "--predefined-pose",
            type=str,
            required=False,
            help="Define the name of the predefined pose you want to execute",
        )
        self.rad_deg = False
        try:
            args = parser.parse_args()
            self.arm_name = args.arm_name
            self.list_arms = args.list_arms
            self.predefined_pose = args.predefined_pose
        except:
            self.list_arms = True

    def print_list_arms(self):
        print("\n---------------------")
        print(f"{self.col.OKBLUE}List of avaliable arms{self.col.ENDC}")
        for c, arm_name in enumerate(self.arms.get_list_of_arms()):
            print(f"{c}. {arm_name}")

    def check_predefined_pose(self):
        if not self.predefined_pose in self.arms.get_list_predefined_poses(
            self.arm_name
        ):
            self.list_predefined_poses()
            raise ValueError(
                f"the predefined_pose {self.predefined_pose} is not avaliable for this arm"
            )

    def list_predefined_poses(self):
        print("\n---------------------")
        print(
            f"{self.col.OKBLUE}List of predefined poses of the arm: {self.arm_name}{self.col.ENDC}"
        )
        print(f"name")
        name_poses = self.arms.get_list_predefined_poses(self.arm_name)
        for joint_name in name_poses:
            print(f"{joint_name}")

    async def execute_predefined_pose(self, predefined_pose: str):
        print(f"\n Start the execution of the predefined pose {predefined_pose}\n")

        await self.arms.set_predefined_pose(
            self.arm_name,
            predefined_pose,
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            wait=True,
        )

    def callback_feedback(self, arg1, arg2):
        print(f"ARM:{arg1} PERCENTAGE:{arg2:.2f}")

    def callback_finish(self, error, error_msg):
        if error == 0:
            print(
                f"\n{self.col.OKGREEN}FINISH SUCCESSFULLY THE EXECUTION OF THE PREDEFINED POSE"
            )
        else:
            print(
                f"\n{self.col.FAIL}ERROR IN THE EXECUTION NUMBER: {error}{self.col.ENDC}"
            )
        print("------------")
        print("")
