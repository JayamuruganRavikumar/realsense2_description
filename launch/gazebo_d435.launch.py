#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro


def generate_launch_description():

    # Get package directories
    pkg_realsense_description = get_package_share_directory('realsense2_description')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    # Paths
    xacro_file = os.path.join(pkg_realsense_description, 'urdf', 'test_d435_camera.urdf.xacro')

    # Process xacro to get URDF
    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={
            'use_nominal_extrinsics': 'true',
            'add_plug': 'false',
            'use_mesh': 'true'
        }
    )
    robot_description = {'robot_description': robot_description_config.toxml()}

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'verbose': 'true'}.items()
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )

    # Spawn the camera in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_realsense_camera',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'realsense_d435',
            '-x', '0',
            '-y', '0',
            '-z', '0.5'  # Spawn 0.5m above ground
        ],
        output='screen'
    )

    # RViz (optional - for visualization)
    rviz_config = os.path.join(pkg_realsense_description, 'rviz', 'urdf.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
        # rviz,  # Uncomment if you want RViz
    ])
