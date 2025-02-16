#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.duration import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import String
from locobot_wrapper_msgs.action import MoveGripper


class LocobotGrip(Node):
    def __init__(self):
        super().__init__('locobot_gripper')
        self.gripper_state = "unknown"

        # Gripper open and close positions
        self.open_positions = [0.10, -0.10]
        self.close_positions =  [1.0e-3, -1.0e-3]

        self.get_logger().info("Gripper Action Server started")

        self.grip_publisher = self.create_publisher(JointTrajectory, '/locobot/gripper_controller/joint_trajectory', 10)
        self.state_publisher = self.create_publisher(String, '/locobot/gripper_state', 10)
        self.start_time = self.get_clock().now()

        # Action Server
        self._action_server = ActionServer(
            self,
            MoveGripper,
            'movegripper',
            self.execute_callback
        )
        

    def execute_callback(self, goal_handle):
        goal = goal_handle.request
        feedback_msg = MoveGripper.Feedback()
        feedback_msg.feedback = f"Processing command: {goal.command}"
        goal_handle.publish_feedback(feedback_msg)
     
        if goal.command.lower() == "open":
            self.get_logger().info("Opening...")
            self.publish_gripper_action(self.open_positions, goal.duration)
            self.gripper_state = "open"
        elif goal.command.lower() == "close":
            self.get_logger().info("Closing...")
            self.publish_gripper_action(self.close_positions, goal.duration)
            self.gripper_state = "close"
        else:
            self.get_logger().info(f"Invalid command: {goal.command}")
            goal_handle.abort()
            self.get_logger().info("Aborting...")
            return MoveGripper.Result(success=False)
        
        self.publish_state(f"Gripper {self.gripper_state}")

        goal_handle.succeed()        
        return MoveGripper.Result(success=True)

    def publish_gripper_action(self, positions, dur):
        gripAction = JointTrajectory()
        gripAction.header.frame_id = ''
        gripAction.joint_names = ['left_finger', 'right_finger']
        
        point = JointTrajectoryPoint()
        point.positions = positions
        # point.velocities = [0.0, 0.0]
        # point.accelerations = [0.0, 0.0]
        point.time_from_start = Duration(seconds=dur).to_msg()
        
        gripAction.points = [point]
        self.grip_publisher.publish(gripAction)

    def publish_state(self, state_message):
        state_msg = String()
        state_msg.data = state_message
        self.state_publisher.publish(state_msg)
        self.get_logger().info(state_message)

def main(args=None):
    rclpy.init(args=args)
    locobot_grip = LocobotGrip()
    rclpy.spin(locobot_grip)
    locobot_grip.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()