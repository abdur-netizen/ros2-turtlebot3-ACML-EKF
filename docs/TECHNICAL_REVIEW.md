# Technical Review: TurtleBot3 EKF + AMCL + Nav2

## Project overview

This workspace implements autonomous TurtleBot3 Burger navigation using ROS 2 Humble, Gazebo, EKF sensor fusion, AMCL localization, Nav2 path planning, and a Python dynamic waypoint controller.

The system has been exercised in real-time Gazebo simulation. The accompanying six-page technical report documents the simulation setup, localization and navigation architecture, engineering resolutions, RViz2 runtime feedback, and a successful five-waypoint mission.

**Terminology:** The localization algorithm is AMCL (Adaptive Monte Carlo Localization), combined with EKF (Extended Kalman Filter) sensor fusion. AMCL and ACML are not interchangeable names.

## Architecture

```text
TurtleBot3 Gazebo
   ├── /odom ───────────────┐
   ├── /imu ────────────────┤
   │                        v
   │                robot_localization EKF
   │                        |
   │                 /odometry/filtered
   │
   ├── /scan ───────────────┐
   │                        v
   │                 Nav2 AMCL + map
   │                        |
   │                   map -> odom
   │
   └── odometry / TF ──> Nav2 costmaps and controller
                              |
                       planner + DWB
                              |
                           /cmd_vel
                              |
                       TurtleBot3 motion

RViz2 /clicked_point ─────────────┐
                                  ├──> waypoint_navigator
/dynamic_waypoints (PoseArray) ───┘          |
                                             v
                                  Nav2 Simple Commander
                                  goThroughPoses(...)
```

## Main packages

### bot_localization

- EKF configuration in `config/ekf.yaml`.
- Nav2 and AMCL configuration in `config/nav2_params.yaml`.
- Occupancy-grid map assets in `maps/`.
- Unified simulation launch in `launch/navigation_sim.launch.py`.
- Launch orchestration includes Gazebo, EKF, Nav2 bringup, and RViz2 with simulation time.

### bot_navigation

- Python navigation controller built with Nav2 Simple Commander.
- Runtime subscription to `/dynamic_waypoints` (`geometry_msgs/msg/PoseArray`).
- Runtime subscription to `/clicked_point` (`geometry_msgs/msg/PointStamped`) for RViz2 Publish Point input.
- Sends waypoint sequences through Nav2's `goThroughPoses()` interface.
- Reports localized pose, remaining distance, and waypoint progress while a route is active.

### bot_description

- Maintains the ROS 2 package structure used alongside the TurtleBot3 model and its published kinematic frames.

## Localization and TF2

The localization pipeline is organized into two stages:

1. **Local odometry fusion — EKF:** `ekf_node` is configured with wheel odometry (`/odom`) and IMU (`/imu`) inputs, planar operation, and a 30 Hz filter frequency. Its filtered odometry output is `/odometry/filtered`.
2. **Global pose correction — AMCL:** AMCL uses the saved occupancy grid and incoming `/scan` data to estimate the robot pose and publish the `map -> odom` transform.

The frame hierarchy used by the navigation system includes `map`, `odom`, `base_footprint`, `base_link`, and the robot sensor frames. The included TF graph is a diagnostic snapshot of this hierarchy.

The Nav2 parameter file retains `/odom` as its odometry topic. The EKF output topic and Nav2 odometry parameter are configuration details worth keeping consistent when adapting the stack to another robot or odometry source.

## Autonomous planning and dynamic waypoint control

Nav2 provides the global and local navigation layers:

- **Global planning:** NavFn plans through the global costmap using the static map and inflation layer.
- **Local control and obstacle avoidance:** DWB evaluates local velocity trajectories against live obstacle observations from the LiDAR-backed costmap and generates `/cmd_vel`.
- **Dynamic waypoint execution:** The Python node accepts updated waypoint goals while running. A `PoseArray` can provide a batch of goals, while RViz2 Publish Point sends individual `PointStamped` goals through `/clicked_point`. Updated goals replace the active route through the navigator's task-cancellation and new-goal flow.

The configured map resolution is 0.05 m/cell. The report describes a 117 × 103 cell map with origin `[-2.93, -2.56, 0.0]`.

## Engineering resolutions documented in the project report

The report describes the following integration issues and their implemented resolutions:

| Issue encountered | Resolution described |
|---|---|
| TF future extrapolation during initial pose setup | Enabled simulation time for BasicNavigator and waited for Gazebo clock updates before publishing the initial pose |
| RViz2 dropping sensor frames | Launched RViz2 directly with simulation time enabled |
| Nav2 lifecycle bringup failure | Used ROS 2 Humble-compatible Nav2 plugin naming and parameters |
| RViz2 resource pressure and hidden robot model | Adjusted RViz2 displays and frame-rate settings; allowed headless Gazebo physics when required |
| Rigid waypoint lists | Added runtime waypoint inputs through `/clicked_point` and `/dynamic_waypoints` |

## Runtime validation and observed results

The supplied technical report records real-time simulation results and includes supporting screenshots:

- **Page 2:** Gazebo view of the TurtleBot3 Burger in the obstacle arena, with LiDAR visualization.
- **Page 5:** RViz2 view showing active Navigation and Localization states, AMCL particles, local/global costmaps, planned trajectory, and live navigation feedback. The displayed feedback includes ETA 7 s, remaining distance 1.67 m, elapsed time 7 s, and one recovery at the captured moment.
- **Page 6:** Terminal output showing Nav2 readiness, traversal of five goals, and the final result `Succeeded! All waypoints traversed.`, alongside the completed RViz2 trajectory.

The report's experiment section also records autonomous obstacle avoidance around the arena pillars and successful activation of the localization and navigation lifecycle managers.

These feedback values are a captured runtime snapshot, not a general performance guarantee for every route or environment.

## Configuration and extension notes

The following are useful engineering considerations when extending or porting the project; they are not descriptions of observed simulation failures:

- Keep the EKF output topic and the odometry topic consumed by Nav2 intentionally aligned.
- Ensure each TF edge has a single authoritative publisher when changing the Gazebo or EKF odometry setup.
- Send dynamic waypoint goals in the navigation map frame, or add TF2 conversion when accepting goals from other frames.
- Keep the saved occupancy map aligned with the selected Gazebo world and spawn pose.
- Keep package runtime dependencies and license metadata current as the workspace evolves.
- Add automated tests for waypoint message handling and route replacement to preserve behavior during future changes.

## Conclusion

The project brings together EKF-based sensor fusion, AMCL global localization, Nav2 obstacle-aware planning, Gazebo simulation, RViz2 visualization, and runtime dynamic waypoint execution for the TurtleBot3 Burger. The supplied runtime report documents real-time simulation, obstacle avoidance, active localization/navigation components, and successful completion of a five-waypoint autonomous mission.
