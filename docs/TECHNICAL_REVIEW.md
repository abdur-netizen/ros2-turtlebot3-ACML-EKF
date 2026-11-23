# Technical Review: TurtleBot3 EKF + AMCL + Nav2

## Scope

Reviewed the uploaded `turtlebot_nav_ws.zip` source, its TF frame snapshot, and the included colcon logs. This is a static source/configuration review; no live ROS 2/Gazebo runtime was available.

The workspace has three packages:
- `bot_localization`: launch file, EKF/AMCL/Nav2 configuration, and a static map.
- `bot_navigation`: Python waypoint navigator using Nav2 Simple Commander.
- `bot_description`: minimal ament_cmake skeleton only; no URDF, meshes, or robot-state-publisher assets.

**Terminology:** The implementation contains EKF configuration and AMCL localization. It does not contain an ACML algorithm. AMCL and ACML are not interchangeable names.

## Architecture observed

```text
TurtleBot3 Gazebo -> /odom ----------------------+
                 -> /imu ------------------------+-> robot_localization/ekf_node
                                                   -> /odometry/filtered
                                                      (not consumed by Nav2 here)

Gazebo TF: odom -> base_footprint -> base_link -> sensors/wheels
Nav2 map_server + AMCL: map + /scan + odom TF -> map -> odom
Nav2 planner/controller -> cmd_vel -> TurtleBot3

RViz /clicked_point --------------------------+
                                               +-> waypoint_navigator
/dynamic_waypoints (PoseArray) ----------------+      |
                                                      v
                                              Nav2 Simple Commander
                                              goThroughPoses(...)
```

The included TF snapshot shows `map -> odom -> base_footprint -> base_link`, with sensor and wheel links below `base_link`. It is one timestamped capture, not proof of continuous runtime health.

## Findings

### Critical — EKF output is not integrated into Nav2 odometry

`config/ekf.yaml` sets `odom0: /odom`, `imu0: /imu`, `frequency: 30.0`, `two_d_mode: true`, and `publish_tf: false`. The default filtered output is `/odometry/filtered`.

The launch file starts `ekf_node`, but does not remap the filtered topic to `/odom` or configure Nav2 to consume `/odometry/filtered`. The Nav2 parameters use `odom_topic: /odom`; the captured TF tree also contains `odom -> base_footprint`.

Thus, the archive proves that the EKF node is launched, but does not establish that its filtered state drives Nav2 localization/control. With `publish_tf: false`, EKF is not publishing the odom-to-base transform. Do not describe this as verified EKF-driven navigation until the data path is wired and tested.

**Recommended action:** choose one authoritative odometry path. Configure EKF to publish the intended `odom -> base_footprint` transform and configure Nav2 to consume filtered odometry, or consistently remap/configure the filtered output as the navigation odometry source. Ensure Gazebo and EKF do not publish the same TF edge. Validate topic publishers and TF ownership at runtime.

### High — Gazebo world and Nav2 map correspondence is unverified

The launch file starts the standard `turtlebot3_world.launch.py`, but Nav2 receives `maps/virtual_world.yaml`. No matching custom Gazebo world file is launched from this package. This may be intentional if the map was generated from the standard world, but the archive does not establish that. Verify geometry, map origin/resolution, occupancy, and robot spawn pose.

### High — Incoming waypoint frame IDs are not transformed

The `PoseArray` and `PointStamped` callbacks carry their incoming frame IDs into Nav2 goals. The node does not transform poses to `map`. External publishers may use `odom` or another frame. Either enforce/reject non-`map` frames or transform each incoming goal with TF2 and suitable timestamp/error handling.

### Medium — YAML waypoints are not consumed

`config/waypoints.yaml` contains an initial pose and five named waypoints. The Python node does not load it; it hard-codes `(-2.0, -0.5, 0.0)` and waits for dynamic topics. The YAML is therefore not an executed route in the current implementation.

### Medium — Route cancellation/preemption is not synchronized

On a new route, the node calls `cancelTask()`, spins once, then immediately submits the new route. It does not wait for a terminal cancellation result. Add a bounded cancellation wait/state check. Empty `PoseArray` messages are ignored, so they cannot clear an existing route.

### Medium — Runtime dependencies are incomplete

The localization launch file directly resolves and launches Gazebo, Nav2 bringup, TurtleBot3 Navigation2, and RViz2, and imports `launch`, `launch_ros`, and `ament_index_python`. The package manifest does not declare all these runtime dependencies. The launch file also resolves `turtlebot3_navigation2` but does not use the variable. The separate `amcl.yaml` is not passed to Nav2; AMCL parameters are duplicated in `nav2_params.yaml`.

### Low — Placeholder and maintainability items

- `bot_description/package.xml` has TODO description/license values and no robot description assets.
- `slam_toolbox` is declared but not launched or referenced.
- Initial pose is duplicated in YAML and Python.
- Heading conversion does not normalize the result to `[-180, 180]`.
- Existing tests are generated lint tests; there are no behavior tests for waypoint frame handling, route replacement, or goal failure.

## Build evidence

The archive's `log/latest_build` points to `build_2026-11-23_16-21-53`. That colcon invocation selects only `bot_navigation`, and its package build command returns code 0. This supports only the claim that the selected package built successfully in that recorded environment. It does not prove a clean full-workspace build, successful launch, or end-to-end navigation.

## Validation checklist

1. Confirm ROS 2 distribution and install runtime dependencies.
2. Run `rosdep install --from-paths src --ignore-src -r -y`.
3. Clean `build/`, `install/`, and `log/`; run `colcon build --symlink-install`.
4. Start the launch file and verify `/clock`, `/scan`, `/odom`, `/imu`, `/odometry/filtered`, `/map`, and Nav2 lifecycle states.
5. Confirm exactly one publisher owns `odom -> base_footprint`.
6. Verify that the static map matches the Gazebo world and initial pose.
7. Test one clicked point, multi-pose route, route preemption, empty route, unreachable goal, and non-map input frame.
8. Record terminal output and RViz/Gazebo evidence.

## Overall assessment

The project is a useful TurtleBot3 simulation/navigation foundation with clear package separation, Nav2 Simple Commander waypoint execution, and a TF snapshot showing the expected frame chain at capture time. The main gap is the unclosed EKF data path: the filter is launched, but its output is not configured as the odometry source consumed by Nav2 or as the base TF publisher. Map/world alignment and waypoint frame handling also require validation before the project can be presented as a fully integrated EKF localization system.
