# RealSense2 Description for Ignition Gazebo

Modified RealSense2 description package for use with Ignition Gazebo (Gazebo Sim). This package provides URDF/xacro files and launch configurations to simulate Intel RealSense D400 series cameras in Gazebo.

## Overview

This package is based on the original `realsense2_description` package but has been adapted to work with Ignition Gazebo using Gazebo sensors to mimic RealSense camera behavior.


## Usage

### Launch Gazebo Simulation

To launch a D435 camera in Gazebo:

```bash
ros2 launch realsense2_description gazebo_sim_d435.launch.py
```

This will:
- Start Gazebo with the RealSense demo world
- Spawn the D435 camera model
- Set up ROS 2 bridges for camera topics
- Publish camera transforms via `robot_state_publisher`

### View Model in RViz

To view the camera model without simulation:

```bash
ros2 launch realsense2_description view_model.launch.py
```

## Published Topics

When running the Gazebo simulation, the following topics are available:

- `/camera/color/image_raw` - RGB image
- `/camera/depth/image_raw` - Depth image
- `/camera/infra1/image_raw` - Left infrared image
- `/camera/infra2/image_raw` - Right infrared image
- `/camera/color/camera_info` - RGB camera calibration
- `/camera/depth/camera_info` - Depth camera calibration

## Credits

Based on the original `realsense2_description` package by Intel RealSense ROS Team.
Modified for Ignition Gazebo compatibility.
