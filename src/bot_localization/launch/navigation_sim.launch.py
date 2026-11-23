import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bot_loc_dir = get_package_share_directory('bot_localization')
    tb3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    tb3_nav2_dir = get_package_share_directory('turtlebot3_navigation2')

    default_map = os.path.join(bot_loc_dir, 'maps', 'virtual_world.yaml')
    ekf_config = os.path.join(bot_loc_dir, 'config', 'ekf.yaml')
    nav2_params = os.path.join(bot_loc_dir, 'config', 'nav2_params.yaml')
    rviz_config = os.path.join(nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')

    map_yaml_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_map_cmd = DeclareLaunchArgument(
        'map',
        default_value=default_map,
        description='Full path to the map YAML file to load',
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true',
    )

    # Set TURTLEBOT3_MODEL automatically for any new terminal session
    set_tb3_model = SetEnvironmentVariable('TURTLEBOT3_MODEL', 'burger')

    # 1. Gazebo Virtual Environment
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb3_gazebo_dir, 'launch', 'turtlebot3_world.launch.py')
        )
    )

    # 2. EKF Local Sensor Fusion (/odom + /imu -> /odometry/filtered)
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config, {'use_sim_time': use_sim_time}],
    )

    # 3. Nav2 + AMCL Global Localization (delayed 5s so Gazebo /clock starts first)
    nav2_launch = TimerAction(
        period=5.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')
                ),
                launch_arguments={
                    'use_sim_time': use_sim_time,
                    'map': map_yaml_file,
                    'params_file': nav2_params,
                }.items(),
            )
        ],
    )

    # 4. RViz2 with explicit use_sim_time=True (prevents Humble rviz_launch.py clock mismatch)
    rviz_node = TimerAction(
        period=6.0,
        actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                arguments=['-d', rviz_config],
                parameters=[{'use_sim_time': True}],
                output='screen',
            )
        ],
    )

    ld = LaunchDescription()
    ld.add_action(declare_map_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(set_tb3_model)
    ld.add_action(gazebo_launch)
    ld.add_action(ekf_node)
    ld.add_action(nav2_launch)
    ld.add_action(rviz_node)

    return ld
