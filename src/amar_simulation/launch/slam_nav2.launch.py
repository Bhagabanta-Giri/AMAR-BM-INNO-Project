import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # Use simulation time across all nodes
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # 1. Nav2 Navigation Launch
    nav2_launch_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'launch')
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_launch_dir, 'navigation_launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # 2. SLAM Toolbox Launch
    slam_launch_dir = os.path.join(get_package_share_directory('slam_toolbox'), 'launch')
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(slam_launch_dir, 'online_async_launch.py')),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'odom_frame': 'odom',
            'base_frame': 'base_footprint',
            'scan_topic': '/scan'
        }.items()
    )

    # 3. RViz2 Launch
    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_launch_dir, 'rviz_launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # # 4. Gazebo world launch
    # gazebo_launch_dir = os.path.join(get_package_share_directory('igvc_simulation'), 'launch')
    # gazebo_launch = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(os.path.join(gazebo_launch_dir, 'gz.launch.py'))
    # )

    # # 5. Spawn Rover launch
    # spawn_rover_launch_dir = os.path.join(get_package_share_directory('igvc_description'), 'launch')
    # spawn_rover_launch = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(os.path.join(spawn_rover_launch_dir, 'spawn_rover.launch.py'))
    # )

    return LaunchDescription([
        # gazebo_launch,
        # spawn_rover_launch,
        nav2_launch,
        slam_launch,
        rviz_launch
    ])