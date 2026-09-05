import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # Use simulation time across all nodes
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Dynamically find the params file instead of hardcoding the home directory
    amar_sim_dir = get_package_share_directory('amar_simulation')
    nav2_params_path = os.path.join(amar_sim_dir, 'params', 'jnav2_params.yaml')

    # 1. Nav2 Navigation Launch
    nav2_launch_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'launch')
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_launch_dir, 'navigation_launch.py')),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': nav2_params_path, # FIX: Changed from 'params' to 'params_file'
        }.items()
    )

    # 2. SLAM Toolbox Launch
    slam_launch_dir = os.path.join(get_package_share_directory('slam_toolbox'), 'launch')
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(slam_launch_dir, 'online_async_launch.py')),
        launch_arguments={
            'use_sim_time': use_sim_time,
            # Note: If SLAM Toolbox requires 'base_footprint' instead of its default 'base_link', 
            # you must pass a custom YAML file using the 'slam_params_file' argument here.
        }.items()
    )

    # 3. RViz2 Launch
    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_launch_dir, 'rviz_launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    return LaunchDescription([
        nav2_launch,
        slam_launch,
        rviz_launch
    ])