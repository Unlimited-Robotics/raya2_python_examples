from raya.application_base import RayaApplicationBase
from raya.controllers.arms_controller import ArmsController
import time

from raya.enumerations import ANG_UNIT


class RayaApplication(RayaApplicationBase):
    async def setup(self):
        self.flag = False
        self.arms = await self.enable_controller("arms")

        print(f"list of arms --> {self.arms.get_list_of_arms()}")
        print("------------")
        print("")

        print(
            f"list of predefined_poses right arm --> {self.arms.get_list_predefined_poses('right_arm')}"
        )
        print("------------")
        print("")

        print(
            f"list of predefined_poses left arm --> {self.arms.get_list_predefined_poses('left_arm')}"
        )
        print("------------")
        print("")

        right_arm = self.arms.get_state_of_arm("right_arm")
        print(f"names of joints: {right_arm['name']}")
        print("")
        print(f"position of joints: {right_arm['position']}")
        print("")
        print(f"velocity of joints: {right_arm['velocity']}")
        print("------------")
        print("")

        left_arm = self.arms.get_state_of_arm("left_arm")
        print(f"names of joints: {left_arm['name']}")
        print("")
        print(f"position of joints: {left_arm['position']}")
        print("")
        print(f"velocity of joints: {left_arm['velocity']}")
        print("------------")
        print("")

        await self.arms.are_joints_position_valid(
            "left_arm",
            ["arm_left_shoulder_FR_joint"],
            [1.07],
            units=ANG_UNIT.RAD,
            callback_finish=self.callback_finish_srv,
        )

        await self.arms.are_joints_position_valid(
            "right_arm",
            ["arm_right_shoulder_FR_joint"],
            [3.07],
            units=ANG_UNIT.RAD,
            wait=True,
            callback_finish=self.callback_finish_srv,
        )

        await self.arms.are_joints_position_valid(
            "left_arm",
            ["arm_left_shoulder_FR_joint"],
            [40],
            callback_finish=self.callback_finish_srv,
        )

        await self.arms.are_joints_position_valid(
            "right_arm",
            ["arm_right_shoulder_FR_joint"],
            [-40],
            callback_finish=self.callback_finish_srv,
        )

        await self.arms.is_pose_valid_q(
            "left_arm",
            x=0.38661,
            y=0.25621,
            z=1.18,
            qx=0.48961,
            qy=0.51048,
            qz=0.51019,
            qw=-0.48929,
            callback_finish=self.callback_finish_srv,
        )

        await self.arms.is_pose_valid_q(
            "right_arm",
            x=0.38661,
            y=-0.25621,
            z=1.18,
            qx=0.48961,
            qy=0.51048,
            qz=0.51019,
            qw=-0.48929,
            callback_finish=self.callback_finish_srv,
        )

        while self.arms.are_checkings_in_progress():
            print("---waiting for checkings finish---")
            await self.sleep(0.5)

        await self.arms.set_pose_q(
            "left_arm",
            x=0.38661,
            y=0.25621,
            z=1.18,
            qx=0.48961,
            qy=0.51048,
            qz=0.51019,
            qw=-0.48929,
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            # wait=True,
        )

        await self.arms.set_pose_q(
            "right_arm",
            x=0.38661,
            y=-0.25621,
            z=1.18,
            qx=0.48961,
            qy=0.51048,
            qz=0.51019,
            qw=-0.48929,
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            # wait=True,
        )

        while self.arms.is_arm_in_execution("right_arm") or self.arms.is_arm_in_execution(
            "left_arm"
        ):
            await self.sleep(0.1)

        await self.arms.set_pose_q(
            "left_arm",
            x=0.28661,
            y=0.25621,
            z=1.18,
            qx=0.48961,
            qy=0.51048,
            qz=0.51019,
            qw=-0.48929,
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            cartesian_path=True,
            wait=True,
        )

        await self.arms.set_pose_q(
            "right_arm",
            x=0.28661,
            y=-0.25621,
            z=1.18,
            qx=0.48961,
            qy=0.51048,
            qz=0.51019,
            qw=-0.48929,
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            cartesian_path=True,
            wait=True,
        )

        await self.arms.set_pose_q(
            "left_arm",
            x=0.28661,
            y=0.25621,
            z=1.48,
            qx=0.48961,
            qy=0.51048,
            qz=0.51019,
            qw=-0.48929,
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            cartesian_path=True,
            wait=True,
        )

        await self.arms.set_pose_q(
            "right_arm",
            x=0.28661,
            y=-0.25621,
            z=1.48,
            qx=0.48961,
            qy=0.51048,
            qz=0.51019,
            qw=-0.48929,
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            cartesian_path=True,
            wait=True,
        )

        await self.arms.set_predefined_pose(
            "right_arm",
            "right_arm_home",
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            wait=True,
        )

        await self.arms.set_predefined_pose(
            "left_arm",
            "left_arm_home",
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            wait=True,
        )

        await self.arms.set_joints_position(
            "right_arm",
            ["arm_right_shoulder_FR_joint"],
            [1.57],
            units=ANG_UNIT.RAD,
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            wait=True,
        )

        await self.arms.set_joints_position(
            "left_arm",
            ["arm_left_shoulder_FR_joint"],
            [1.57],
            units=ANG_UNIT.RAD,
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            wait=True,
        )

        await self.arms.set_joints_position(
            "right_arm",
            ["arm_right_shoulder_FR_joint"],
            [15],
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            wait=True,
        )

        await self.arms.set_joints_position(
            "left_arm",
            ["arm_left_shoulder_FR_joint"],
            [15],
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            wait=True,
        )

    async def loop(self):
        self.finish_app()

    async def finish(self):
        print("finishing")

    def callback_feedback(self, arg1, arg2):
        print(f"ARM:{arg1} PERCENTAGE:{arg2:.2f}")

    def callback_finish(self, arg1, arg2):
        print(f"FINISH ACTION / ERROR: {arg1} ERROR_MSG: {arg2}")
        print("------------")
        print("")

    def callback_finish_srv(self, arg1, arg2, arg3):
        if arg3 != '':
            print(f"FINISH SERVICE / ERROR: {arg1} ERROR_MSG: {arg2} DISTANCE: {arg3:.2f}")
        else:
            print(f"FINISH SERVICE / ERROR: {arg1} ERROR_MSG: {arg2}")
        print("------------")
        print("")
