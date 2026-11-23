# TurtleBot3 ROS 2 Navigation with EKF and AMCL

A ROS 2 workspace for TurtleBot3 simulation and navigation using Gazebo, robot_localization EKF configuration, AMCL, Nav2, and a dynamic waypoint navigator.

> **Implementation note:** The current source implements EKF configuration plus AMCL localization. It does not contain an ACML algorithm. The repository name is retained as requested; the implementation is described according to the code actually present.

## Workspace layout

```text
turtlebot_nav_ws/
├── src/
│   ├── bot_description/             # Minimal ament_cmake package skeleton
│   ├── bot_localization/
│   │   ├── config/                  # EKF, AMCL and Nav2 parameters
│   │   ├── launch/navigation_sim.launch.py
│   │   └── maps/                    # virtual_world.png + YAML metadata
│   └── bot_navigation/
│       ├── bot_navigation/waypoint_navigator.py
│       └── config/waypoints.yaml
└── docs/
    ├── TECHNICAL_REVIEW.md
    └── diagnostics/tf_tree_2026-11-23.gv
```

## Software architecture

1. **Simulation:** the launch file includes the standard TurtleBot3 Gazebo world launch.
2. **Local state estimation:** `robot_localization/ekf_node` is started with wheel odometry (`/odom`) and IMU (`/imu`) inputs.
3. **Global localization and navigation:** Nav2 bringup is delayed to allow the simulation clock to start. The supplied map YAML and Nav2 parameter file are passed to bringup.
4. **Visualization:** RViz2 is started with simulation time enabled.
5. **Waypoint execution:** `waypoint_navigator` uses Nav2 Simple Commander and accepts `geometry_msgs/PoseArray` on `/dynamic_waypoints` and `geometry_msgs/PointStamped` on `/clicked_point`.

## Requirements

The workspace targets ROS 2 with the following packages installed in the environment:

- TurtleBot3 simulation packages (`turtlebot3_gazebo`)
- TurtleBot3 model configuration (`TURTLEBOT3_MODEL=burger`)
- `robot_localization`
- `nav2_bringup`, `nav2_amcl`, `nav2_map_server`, `nav2_simple_commander`
- `rviz2`
- ROS 2 Python packages for `rclpy` and `geometry_msgs`

The exact ROS 2 distribution and package versions were not declared in the uploaded source archive. Confirm package availability for your installed distribution before running.

## Build

From the workspace root:

```bash
source /opt/ros/<your_ros2_distro>/setup.bash
export TURTLEBOT3_MODEL=burger
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

The uploaded archive contains a latest build log showing a successful build of the `bot_navigation` package selected by itself. This is not evidence of a clean full-workspace build or a complete end-to-end navigation test.

## Run

In a sourced terminal:

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch bot_localization navigation_sim.launch.py
```

In another sourced terminal:

```bash
ros2 run bot_navigation waypoint_navigator
```

Use RViz2's **Publish Point** tool to send a point to `/clicked_point`, or publish a `geometry_msgs/msg/PoseArray` to `/dynamic_waypoints`.

Example topic inspection:

```bash
ros2 topic list
ros2 topic echo /odom
ros2 topic echo /imu
ros2 topic echo /odometry/filtered
ros2 run tf2_tools view_frames
```

## Important integration caveats

Read [docs/TECHNICAL_REVIEW.md](docs/TECHNICAL_REVIEW.md) before treating this as a verified EKF-driven navigation pipeline. In particular, the current EKF output and TF configuration are not wired into Nav2's configured odometry input. The custom map is passed to Nav2, while Gazebo is launched using the standard TurtleBot3 world; map/world correspondence must be checked.

## License

Package manifests currently declare Apache-2.0 for `bot_navigation` and `bot_localization`. The `bot_description` skeleton still has a TODO license field. Confirm and standardize licensing before redistribution.
