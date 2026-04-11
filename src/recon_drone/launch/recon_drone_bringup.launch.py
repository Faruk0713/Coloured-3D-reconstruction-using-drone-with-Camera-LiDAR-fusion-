import os
import xacro
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_recon = get_package_share_directory('recon_drone')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    yaml_file = os.path.join(pkg_recon, 'config', 'recon_drone.yaml')
    xacro_file = os.path.join(pkg_recon, 'urdf', 'recon_drone.urdf.xacro')

    robot_desc = xacro.process_file(
        xacro_file,
        mappings={'params_path': yaml_file}
    ).toxml()

    with open(yaml_file, 'r') as f:
        model_ns = yaml.load(f, Loader=yaml.FullLoader)['namespace']

    world_file = os.path.join(
        get_package_share_directory('sjtu_drone_description'),
        'worlds', 'playground.world'
    )

    return LaunchDescription([

        # Start Gazebo server with our world
        ExecuteProcess(
            cmd=[
                'gzserver', '--verbose', world_file,
                '-s', 'libgazebo_ros_factory.so',
                '-s', 'libgazebo_ros_init.so'
            ],
            output='screen'
        ),

        # Start Gazebo client (GUI)
        ExecuteProcess(
            cmd=['gzclient', '--verbose'],
            output='screen'
        ),

        # Robot state publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='recon_drone_state_publisher',
            namespace=model_ns,
            parameters=[{
                'robot_description': robot_desc,
                'frame_prefix': model_ns + '/'
            }],
            output='screen'
        ),

        # Spawn recon_drone
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-topic', f'/{model_ns}/robot_description',
                '-entity', 'recon_drone',
                '-x', '0.0',
                '-y', '0.0',
                '-z', '0.5'
            ],
            output='screen'
        ),

        # Static transform
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'world', f'{model_ns}/odom'],
            output='screen'
        ),

        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen'
        ),
    ])