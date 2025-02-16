#!/usr/bin/env python3

import os

import launch
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_prefix


def generate_launch_description():
    # Declare launch arguments
    package_name = 'locobot_wrapper'

    package_prefix = get_package_prefix(package_name)

    # Navigate back to 'src' instead of 'install'
    workspace_src = os.path.abspath(os.path.join(package_prefix, "../../src"))
    package_path = os.path.join(workspace_src, package_name)

    param_file = os.path.join(package_path, 'config', 'publish_semantic.yaml')
    
    return LaunchDescription([
        DeclareLaunchArgument('use_sim', default_value='true', description='Whether to use simulation or not'),

        # Log the 'use_sim' parameter to confirm it
        LogInfo(
            condition=IfCondition(LaunchConfiguration('use_sim')),
            msg="use_sim parameter is set to True: Launching additional nodes"
        ),
        LogInfo(
            condition=IfCondition(LaunchConfiguration('use_sim')),
            msg="Launching pose_behavior_node with simulation..."
        ),
        
        # Launch the Arm Control node
        Node(
            package='locobot_wrapper',
            executable='arm_control_wrapper.py',
            name='arm_control_wrapper',
            output='screen',
            parameters=[{'use_sim': LaunchConfiguration('use_sim')}],
        ),

        # publishing the semantic robot description (bit of a hack)
        Node(
            package='locobot_wrapper',
            executable='publish_robot_description_semantic.py',
            name='publish_robot_description_semantic',
            output='screen',
            parameters=[param_file]
        ),

        # Only launch move_arm_action_server if use_sim is True
        Node(
            package='locobot_wrapper',
            executable='move_arm_action_server',
            name='move_arm_action_server',
            output='screen',
            condition=IfCondition(LaunchConfiguration('use_sim'))
        ),

        Node(
            package='locobot_wrapper',
            executable='move_gripper_action_server.py',
            name='move_gripper_action_server',
            output='screen',
            condition=IfCondition(LaunchConfiguration('use_sim'))
        ),
        Node(
            package="topic_tools",
            executable="relay",
            name="relay_node",
            arguments=["/locobot/robot_description", "/robot_description"],
            output="screen",
        ),
    ])
