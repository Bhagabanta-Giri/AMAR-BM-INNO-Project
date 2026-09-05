#!/usr/bin/env python3

# Copyright 2019 ROBOTIS CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Joep Tool, Hyungyu Kim

import os
from os.path import join
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    AppendEnvironmentVariable,
    TimerAction
)
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

def generate_launch_description():
    amar_simulation = get_package_share_directory("amar_simulation")
    world_file = LaunchConfiguration(
        "world_file", 
        default=join(amar_simulation, "worlds", "turtlebot3_house.world")
    )

    gz_sim_share = get_package_share_directory("ros_gz_sim")
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            join(gz_sim_share, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={
            "gz_args": PythonExpression(["'", world_file, " -r'"])
        }.items(),
    )
    
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='rover_bridge',
        parameters=[{
            'config_file': os.path.join(amar_simulation, 'params', 'turtlebot3_burger_cam_bridge.yaml'),
            'qos_overrides./tf_static.publisher.durability': 'transient_local',
            'use_sim_time': True
        }],
        output='screen'
    )


    return LaunchDescription([
        # Set resource paths for Gazebo
        AppendEnvironmentVariable(
            name="GZ_SIM_RESOURCE_PATH",
            value=join(amar_simulation, "worlds")
        ),
        AppendEnvironmentVariable(
            name="GZ_SIM_RESOURCE_PATH",
            value=join(amar_simulation, "models")
        ),
        # Declare launch arguments
        DeclareLaunchArgument("world_file", default_value=world_file),
        
        # Launch Gazebo
        gz_sim,
        bridge,
    ])