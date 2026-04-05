#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
from pathlib import Path
import xacro


def generate_launch_description():

    # Get package directories
    pkg_realsense_description = get_package_share_directory('realsense2_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Paths
    xacro_file = os.path.join(pkg_realsense_description, 'urdf', 'd435_gazebo_sim.urdf.xacro')
    world_file = os.path.join(pkg_realsense_description, 'worlds', 'realsense_demo.sdf')

    # Process xacro to URDF
    robot_description_content = xacro.process_file(xacro_file).toxml()
    robot_description = {'robot_description': robot_description_content}

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )

    gazebo_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=[str(Path(pkg_realsense_description).parent.resolve())]
        )


    # Gazebo Sim launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f'-v 4 -r {world_file}'
        }.items()
    )

    # Spawn the robot
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'realsense_d435',
            '-allow_renaming', 'true',
        ],
        output='screen'
    )

    # Bridge for color camera image
    bridge_camera_color = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera/color/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
        ],
        output='screen'
    )

    # Bridge for infrared cameras
    bridge_camera_infra1 = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera/infra1/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
        ],
        output='screen'
    )

    bridge_camera_infra2 = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera/infra2/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
        ],
        output='screen'
    )

    # Bridge for camera info (color only)
    bridge_camera_info = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera/color/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
        ],
        output='screen'
    )

    # Bridge for RGBD camera (depth image, point cloud, camera info)
    bridge_camera_rgbd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera/rgbd/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/rgbd/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/rgbd/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/camera/rgbd/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
        ],
        output='screen'
    )
    # Static transform: map Gazebo's auto-generated sensor frame to the URDF depth frame
    # camera_depth_frame has X-forward (Gazebo convention), matching the rgbd sensor orientation
    static_tf_rgbd = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0',
                   'camera_depth_frame',
                   'realsense_d435/base_link/camera_rgbd'],
        output='screen'
    )

    # Bridge TF from Gazebo so RViz gets the scoped frame names (realsense_d435/...)
    bridge_tf = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/tf_static@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],
        output='screen'
    )

    # RViz (optional)
    rviz_config = os.path.join(pkg_realsense_description, 'rviz', 'gazebo_sim.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        gazebo_resource_path,
        gazebo,
        robot_state_publisher,
        spawn_entity,
        bridge_camera_color,
        bridge_camera_rgbd,
        bridge_camera_infra1,
        bridge_camera_infra2,
        bridge_camera_info,
        bridge_tf,
        static_tf_rgbd,
        # rviz,  # Uncomment to launch RViz
    ])
