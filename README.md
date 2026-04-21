# 🚁 Coloured 3D Reconstruction Using Drone with Camera-LiDAR Fusion

A ROS2 project that builds a coloured 3D point cloud map by fusing Camera and LiDAR data from a simulated drone.

---

## ⚙️ Requirements

- Ubuntu 22.04
- ROS2 Humble
- Gazebo 11
- Python 3.10+

---

## 📦 Install Dependencies

```bash
# ROS2 packages
sudo apt install ros-humble-velodyne ros-humble-velodyne-gazebo-plugins \
                 ros-humble-xacro ros-humble-robot-state-publisher \
                 ros-humble-cv-bridge ros-humble-pcl-ros \
                 ros-humble-kiss-icp

# Python packages
pip install open3d numpy opencv-python kiss-icp
```

---

## 🔧 Build

```bash
# Clone the repo
git clone https://github.com/Faruk0713/Coloured-3D-reconstruction-using-drone-with-Camera-LiDAR-fusion-.git
cd Coloured-3D-reconstruction-using-drone-with-Camera-LiDAR-fusion-
git checkout drone-ws

# Install dependencies & build
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

---

## 🚀 Running the Project

Open **4 terminals** and run one command in each. Source the workspace in each terminal first:
```bash
source install/setup.bash
```

| Terminal | Command |
|----------|---------|
| 1 | `ros2 launch recon_drone recon_drone_bringup.launch.py` |
| 2 | `ros2 launch kiss_icp odometry.launch.py topic:=/velodyne_points base_frame:=recon_drone/base_link use_sim_time:=true visualize:=false` |
| 3 | `ros2 run lidar_test rgbd_processor` |
| 4 | `python3 src/recon_drone/scripts/teleop_recon_drone.py` |

> ⚠️ Wait for Gazebo to fully load (Terminal 1) before starting the others.

---

## 🗺️ Visualizing in RViz2

```bash
python3 pcd_to_rviz.py
```

In the RViz2 window:
1. Set **Fixed Frame** to `odom_lidar`
2. Click **Add → By Topic → rgbd_map → PointCloud2 → OK**
3. Navigate the drone through the world using Terminal 4
4. The reconstructed coloured 3D world will appear live in RViz2
