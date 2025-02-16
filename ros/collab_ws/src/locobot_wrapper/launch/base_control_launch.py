#!/usr/bin/env python3

import launch
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Declare launch arguments
    
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
            executable='base_control_wrapper.py',
            name='base_control_wrapper',
            output='screen',
            parameters=[{'use_sim': LaunchConfiguration('use_sim')}],
        ),
    ])
