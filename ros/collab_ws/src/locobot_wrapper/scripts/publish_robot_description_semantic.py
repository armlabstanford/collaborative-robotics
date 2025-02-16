#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String  # Change the message type if needed
from rclpy.qos import QoSProfile, QoSDurabilityPolicy

class ParamPublisher(Node):
    def __init__(self):
        """
        This node is a bit of a hack because of Moveit2's issues. 

        Moveit2 requires the robot_description_semantic parameter to be set, but you cannot
        specify the namespace in which you can look for the parameter. This node takes the yaml
        file params, loads it, and republishes it to the topic moveit looks for.

        """
        super().__init__("param_publisher")

        # Declare and get the parameter
        self.declare_parameter("robot_description_semantic", "default_value")  # Default value if not set
        param_value = self.get_parameter("robot_description_semantic").value

        # Set QoS profile to Transient Local
        qos_profile = QoSProfile(
            depth=10,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL
        )

        # Create a publisher with the corrected QoS
        self.publisher_ = self.create_publisher(String, "/robot_description_semantic", qos_profile)

        # # Publish the parameter value periodically
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.msg = String()
        self.msg.data = str(param_value)

    def timer_callback(self):
        """
        publish data to the topic
        """
        self.publisher_.publish(self.msg)

def main(args=None):
    rclpy.init(args=args)
    node = ParamPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
