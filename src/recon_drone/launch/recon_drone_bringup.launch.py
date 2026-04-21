import os
import xacro
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node

def generate_launch_description():
    pkg_recon      = get_package_share_directory('recon_drone')
    pkg_lidar_test = get_package_share_directory('lidar_test')
    yaml_file  = os.path.join(pkg_recon, 'config', 'recon_drone.yaml')
    xacro_file = os.path.join(pkg_recon, 'urdf', 'recon_drone.urdf.xacro')
    robot_desc = xacro.process_file(
        xacro_file,
        mappings={'params_path': yaml_file}
    ).toxml()
    with open(yaml_file, 'r') as f:
        model_ns = yaml.load(f, Loader=yaml.FullLoader)['namespace']
    world_file = os.path.join(pkg_lidar_test, 'worlds', 'building_test.world')

    return LaunchDescription([
        ExecuteProcess(
            cmd=[
                'gzserver', '--verbose', world_file,
                '-s', 'libgazebo_ros_factory.so',
                '-s', 'libgazebo_ros_init.so'
            ],
            additional_env={
                'LIBGL_ALWAYS_SOFTWARE':    '1',
                'MESA_GL_VERSION_OVERRIDE': '3.3',
                'GAZEBO_MODEL_PATH': (
                    '/usr/share/gazebo-11/models:'
                    '/home/hailhydra/lidar_ws/src/sjtu_drone/'
                    'sjtu_drone_description/models'
                ),
            },
            output='screen'
        ),
        ExecuteProcess(
            cmd=['gzclient', '--verbose'],
            additional_env={
                'LIBGL_ALWAYS_SOFTWARE':    '1',
                'MESA_GL_VERSION_OVERRIDE': '3.3',
                'DISPLAY': ':0',
            },
            output='screen'
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='recon_drone_state_publisher',
            namespace=model_ns,
            parameters=[{
                'robot_description': robot_desc,
                'frame_prefix':      model_ns + '/',
                'use_sim_time':      True,
            }],
            output='screen'
        ),
        # Static TF: world → recon_drone/odom (unchanged)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=[
                '0', '0', '0', '0', '0', '0',
                'world', f'{model_ns}/odom'
            ],
            output='screen'
        ),
        # REMOVED: world_to_odom_lidar — causes TF cycle, don't add it
        Node(
            package='topic_tools',
            executable='relay',
            name='odom_relay',
            arguments=[f'/{model_ns}/odom', '/odom'],
            output='screen'
        ),
        Node(
            package='topic_tools',
            executable='relay',
            name='lidar_relay',
            arguments=[f'/{model_ns}/lidar/points', '/velodyne_points'],
            output='screen'
        ),
        # Spawn drone at T+5s
        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package='gazebo_ros',
                    executable='spawn_entity.py',
                    arguments=[
                        '-topic', f'/{model_ns}/robot_description',
                        '-entity', 'recon_drone',
                        '-x', '0.0',
                        '-y', '0.0',
                        '-z', '0.5',
                    ],
                    output='screen'
                ),
            ]
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            parameters=[{'use_sim_time': True}]
        ),
    ])