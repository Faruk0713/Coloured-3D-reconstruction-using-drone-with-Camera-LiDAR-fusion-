import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg = get_package_share_directory('lidar_bot')

    xacro_file = os.path.join(pkg, 'urdf', 'lidar_bot.urdf.xacro')
    robot_desc = xacro.process_file(xacro_file).toxml()

    return LaunchDescription([

        # Publish robot state
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='lidar_bot_state_publisher',
            parameters=[{'robot_description': robot_desc}],
            output='screen'
        ),

        # Spawn into the already-running Gazebo
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-topic', 'robot_description',
                '-entity', 'lidar_bot',
                '-x', '0.0',   # was 0.0
                '-y', '0.0',   # was 0.0
                '-z', '0.1'
            ],
            output='screen'
        ),
    ])