import os
import xacro
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg = get_package_share_directory('recon_drone')

    yaml_file = os.path.join(pkg, 'config', 'recon_drone.yaml')
    xacro_file = os.path.join(pkg, 'urdf', 'recon_drone.urdf.xacro')

    robot_desc = xacro.process_file(
        xacro_file,
        mappings={'params_path': yaml_file}
    ).toxml()

    with open(yaml_file, 'r') as f:
        model_ns = yaml.load(f, Loader=yaml.FullLoader)['namespace']

    return LaunchDescription([

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='recon_drone_state_publisher',
            namespace=model_ns,
            parameters=[{'robot_description': robot_desc,
                         'frame_prefix': model_ns + '/'}],
            output='screen'
        ),

        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-topic', f'/{model_ns}/robot_description',
                '-entity', 'recon_drone',
                '-x', '2.0',
                '-y', '2.0',
                '-z', '1.0'
            ],
            output='screen'
        ),
    ])