#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from interbotix_xs_modules.xs_robot.locobot import InterbotixLocobotXS


class BaseWrapperNode(Node):
    def __init__(self):
        super().__init__('base_wrapper_node')
         # Declare the parameter 'use_sim' with a default value of False
        self.declare_parameter('use_sim', True)
        
        # Get the parameter value
        self.use_sim = self.get_parameter('use_sim').get_parameter_value().bool_value
        
        # Log the value of 'use_sim'
        self.get_logger().info(f"use_sim parameter set to: {self.use_sim}")

        self.twist_publisher = self.create_publisher(Twist, '/locobot/diffdrive_controller/cmd_vel_unstamped', 10)

        self.twist_subscriber = self.create_subscription(
            Twist,
            '/base_twist',
            self.twist_callback,
            10
        )

        if not self.use_sim:
            self.locobot = InterbotixLocobotXS(
            robot_model='locobot_wx250s',
            robot_name='locobot',
            arm_model='mobile_wx250s'
            )

    def twist_callback(self, msg):
        """
        twist callback for the locobot base.
        """
        self.get_logger().info(f"Received twist Message: {msg.linear.x}, {msg.linear.y}, {msg.linear.z}, {msg.angular.x}, {msg.angular.y}, {msg.angular.z}")

        if self.use_sim:
            # directly publish the twist message
            self.twist_publisher.publish(msg)
        else:
            # real world control
            x_vel = msg.linear.x
            turn = msg.angular.z
            self.locobot.base.command_velocity(x_vel, turn)

def main(args=None):
    rclpy.init(args=args)
    node = BaseWrapperNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
