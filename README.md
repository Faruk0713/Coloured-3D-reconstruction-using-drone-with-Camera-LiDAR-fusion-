# ROS 2 Drone Workspace

A ROS 2 (Humble) workspace with Gazebo simulation for drone development.

## Packages
- **sjtu_drone** — Base quadrotor simulator (submodule)
- **recon_drone** — Recon drone with Velodyne VLP-16 LiDAR + cameras
- **lidar_drone** — Experimental drone with LiDAR
- **lidar_bot** — Differential drive robot with Velodyne LiDAR

## Setup
```bash
git clone --recurse-submodules <your-repo-url>
cd ros2_ws
rosdep install -r -y --from-paths src --ignore-src --rosdistro humble
colcon build
source install/setup.bash
```

## Launch
```bash
ros2 launch recon_drone recon_drone_bringup.launch.py
```
