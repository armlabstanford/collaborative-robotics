#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from interbotix_xs_modules.xs_robot.locobot import InterbotixLocobotXS
from locobot_wrapper_msgs.action import MoveArm, MoveGripper
from rclpy.action import ActionClient
from scipy.spatial.transform import Rotation as R
import numpy as np
from std_msgs.msg import Bool


class ArmWrapperNode(Node):
    def __init__(self):
        super().__init__('arm_wrapper_node')
         # Declare the parameter 'use_sim' with a default value of False
        self.declare_parameter('use_sim', False)
        
        # Get the parameter value
        self.use_sim = self.get_parameter('use_sim').get_parameter_value().bool_value
        
        # Log the value of 'use_sim'
        self.get_logger().info(f"use_sim parameter set to: {self.use_sim}")

        self.pose_subscriber = self.create_subscription(
            PoseStamped,
            '/arm_pose',  
            self.pose_callback,
            10
        )

        self.gripper_subscriber = self.create_subscription(
            Bool,
            '/gripper',
            self.gripper_callback,
            10
        )

        self._action_client = ActionClient(
            self,
            MoveArm,
            'movearm'
        )

        self.__gripper_client = ActionClient(
            self,
            MoveGripper,
            'movegripper'
        )

        if not self.use_sim:
            self.locobot = InterbotixLocobotXS(
            robot_model='locobot_wx250s',
            robot_name='locobot',
            arm_model='mobile_wx250s'
            )

    def pose_callback(self, msg):
        # Log the received PoseStamped message
        self.get_logger().info(f"Received Pose: {msg.pose.position.x}, {msg.pose.position.y}, {msg.pose.position.z}")
        # Conditional behavior based on the 'use_sim' parameter
        if self.use_sim:
            # Simulated behavior
            self.get_logger().info(f"Simulated behavior: Moving in simulation with Pose {msg.pose}")
            r = R.from_quat([msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z, msg.pose.orientation.w])
            eul = r.as_euler('xyz', degrees=True)
            goal_msg = MoveArm.Goal()
            goal_msg.pose = [msg.pose.position.x, msg.pose.position.y, msg.pose.position.z, eul[0], eul[1], eul[2]]

            self.send_goal_future = self._action_client.send_goal_async(
                goal_msg,
                feedback_callback=self.feedback_callback
            )
            self.send_goal_future.add_done_callback(self.goal_response_callback)

        else:
            # Actual behavior
            self.get_logger().info(f"Real behavior: Moving hardware with Pose {msg.pose}")
            r = R.from_quat([msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z, msg.pose.orientation.w])
            rot_mat = r.as_matrix()
            matrix = np.ones((4,4))
            matrix[0:3, 0:3] = rot_mat
            matrix[0,3] = msg.pose.position.x
            matrix[1,3] = msg.pose.position.y
            matrix[2,3] = msg.pose.position.z

            self.locobot.arm.set_ee_pose_matrix(matrix,execute=True)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal Rejected')
            return 
        
        self.get_logger().info('Goal Accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
    
    def feedback_callback(self, feedback_msg):
        self.get_logger().info(f"Recieved feedback: {feedback_msg.feedback.progress}")
        
    def gripper_callback(self, msg):
        if self.use_sim:
            goal_msg = MoveArm.Goal()
            if msg.data:

                goal_msg.command = 'open'
                goal.duration = 3.0
            else:
                goal_msg.command = 'closed'
                goal.duration = 3.0
            self.send_gripper_future = self._gripper_client.send_goal_async(
                goal_msg,
                feedback_callback=self.feedback_callback
            )
            self._send_gripper_future.add_done_callback(self.gripper_response_callback)
        else:
            if msg.data:
                self.locobot.gripper.release()
            else:
                self.locobot.gripper.grasp()

    def gripper_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal Rejected')
            return 
        
        self.get_logger().info('Goal Accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

def main(args=None):
    rclpy.init(args=args)
    node = ArmWrapperNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
