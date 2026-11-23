# TurtleBot3 ROS 2 Autonomous Localization and Dynamic Waypoint Navigation

A ROS 2 Humble workspace for TurtleBot3 Burger simulation and autonomous navigation using Gazebo, Extended Kalman Filter (EKF) sensor fusion, Adaptive Monte Carlo Localization (AMCL), Nav2 path planning, and runtime dynamic waypoint control.

The project has been exercised in real-time Gazebo simulation. The accompanying technical report records autonomous obstacle avoidance, active Nav2 localization/navigation lifecycle states, live RViz2 localization and navigation feedback, and successful completion of a five-waypoint mission.

> **Terminology:** The localization algorithm in this project is AMCL (Adaptive Monte Carlo Localization), used together with EKF sensor fusion. The repository name is retained as created.

## Workspace layout

```text
turtlebot_nav_ws/
├── src/
│   ├── bot_description/
│   ├── bot_localization/
│   │   ├── config/                  # EKF and Nav2/AMCL parameters
│   │   ├── launch/navigation_sim.launch.py
│   │   └── maps/                    # virtual_world map and metadata
│   └── bot_navigation/
│       ├── bot_navigation/waypoint_navigator.py
│       └── config/                  # waypoint and route configuration
└── docs/
    ├── TECHNICAL_REVIEW.md
    └── diagnostics/tf_tree_2026-11-23.gv
```

## System architecture

1. **Simulation:** Gazebo runs the TurtleBot3 Burger in the `turtlebot3_world` environment.
2. **Sensor fusion:** `robot_localization/ekf_node` is configured to fuse wheel odometry (`/odom`) and IMU measurements (`/imu`).
3. **Global localization:** Nav2 AMCL estimates the robot pose against the saved occupancy-grid map using the 2D LiDAR scan (`/scan`).
4. **Path planning and obstacle avoidance:** Nav2 global and local costmaps, the NavFn planner, and DWB controller support autonomous navigation around obstacles.
5. **Visualization:** RViz2 displays the map, robot model, AMCL particle cloud, costmaps, planned path, and navigation feedback.
6. **Dynamic waypoint execution:** The Python navigator uses Nav2 Simple Commander and accepts runtime goals through:
   - `/dynamic_waypoints` — `geometry_msgs/msg/PoseArray`
   - `/clicked_point` — `geometry_msgs/msg/PointStamped`, including RViz2 Publish Point input.

## Runtime validation

The accompanying report, *TurtleBot3 Autonomous Localization and Dynamic Waypoint Navigation Technical Report*, records the following simulation results:

- Gazebo simulation of the TurtleBot3 Burger in the obstacle-populated arena.
- Nav2 Navigation and Localization lifecycle indicators active in RViz2.
- AMCL particle-cloud visualization and local/global costmap obstacle inflation.
- Autonomous obstacle avoidance around the arena pillars.
- Live navigation feedback including ETA, remaining distance, elapsed time, and recovery count.
- A five-waypoint autonomous mission ending with the terminal result: `Succeeded! All waypoints traversed.`
- Runtime dynamic waypoint interfaces through `/clicked_point` and `/dynamic_waypoints`.

<img width="1366" height="768" alt="Screenshot from 2026-11-23 16-27-30" src="https://github.com/user-attachments/assets/c372c888-5671-450d-aa1c-84893546376a" />
<img width="1366" height="768" alt="Screenshot from 2026-11-23 16-27-40" src="https://github.com/user-attachments/assets/d1605fde-5dc3-478b-bfe1-7e4483684cef" />


## Requirements

The workspace targets ROS 2 Humble on Ubuntu 22.04 and uses:

- TurtleBot3 simulation packages (`turtlebot3_gazebo`)
- TurtleBot3 Burger model (`TURTLEBOT3_MODEL=burger`)
- `robot_localization`
- `nav2_bringup`, `nav2_amcl`, `nav2_map_server`, `nav2_simple_commander`
- `rviz2`
- ROS 2 Python packages including `rclpy` and `geometry_msgs`

## Build

From the workspace root:

```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## Run the simulation

In a sourced terminal:

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch bot_localization navigation_sim.launch.py
```

In another sourced terminal:

```bash
source /opt/ros/humble/setup.bash
source ~/turtlebot_nav_ws/install/setup.bash
ros2 run bot_navigation waypoint_navigator
```

Use RViz2's **Publish Point** tool to send a point to `/clicked_point`, or publish a `geometry_msgs/msg/PoseArray` to `/dynamic_waypoints`.

Useful inspection commands:

```bash
ros2 topic list
ros2 topic echo /odom
ros2 topic echo /imu
ros2 topic echo /odometry/filtered
ros2 run tf2_tools view_frames
```

## Technical documentation

See [docs/TECHNICAL_REVIEW.md](docs/TECHNICAL_REVIEW.md) for the architecture, configuration notes, runtime validation summary, and suggested areas for future extension.

## License

Package manifests declare Apache-2.0 for the localization and navigation packages. Review package-level license metadata before redistribution.
