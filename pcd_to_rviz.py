"""
pcd_to_rviz.py
--------------
Reads colored_map_v3.pcd and publishes it as a PointCloud2 topic
so you can visualise it in RViz2.

Usage
-----
  Terminal 1:  ros2 run rviz2 rviz2
  Terminal 2:  python3 pcd_to_rviz.py

In RViz2:
  - Fixed Frame  → map   (or odom if map doesn't work)
  - Add → PointCloud2 → topic: /pcd_map
  - Color Transformer → RGB8
  - Size → 0.03
"""

import struct
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
import os

PCD_FILE = os.path.expanduser('~/rgbd_map.pcd')
PUBLISH_TOPIC = '/pcd_map'
FRAME_ID = 'map'
PUBLISH_HZ = 1.0   # republish every second so RViz never loses it


def read_pcd_xyzrgb(path: str) -> np.ndarray:
    """
    Read a binary_little_endian PCD with fields x y z rgb.
    Returns Nx4 float32 array [x, y, z, rgb_packed_as_float].
    """
    with open(path, 'rb') as f:
        # Parse ASCII header
        header = {}
        while True:
            line = f.readline().decode('ascii').strip()
            if line == 'DATA binary_little_endian':
                break
            if line.startswith('POINTS'):
                header['points'] = int(line.split()[1])
            elif line.startswith('FIELDS'):
                header['fields'] = line.split()[1:]
            elif line.startswith('SIZE'):
                header['size'] = list(map(int, line.split()[1:]))

        n = header['points']
        # Each point: x(4) y(4) z(4) rgb(4) = 16 bytes
        data = f.read(n * 16)

    arr = np.frombuffer(data, dtype=np.float32).reshape(n, 4)
    return arr   # [x, y, z, rgb_float]


def make_pointcloud2(xyzrgb: np.ndarray, frame_id: str) -> PointCloud2:
    """
    Build a PointCloud2 message from Nx4 float32 [x, y, z, rgb_packed].
    Uses the standard PCL XYZRGB layout so RViz RGB8 transformer works.
    """
    n = len(xyzrgb)

    # PCL XYZRGB layout: x(4) y(4) z(4) pad(4) rgb(4) pad(12) = 32 bytes/pt
    # Simpler: use unordered x y z rgb in 16 bytes — RViz handles this fine
    fields = [
        PointField(name='x',   offset=0,  datatype=PointField.FLOAT32, count=1),
        PointField(name='y',   offset=4,  datatype=PointField.FLOAT32, count=1),
        PointField(name='z',   offset=8,  datatype=PointField.FLOAT32, count=1),
        PointField(name='rgb', offset=12, datatype=PointField.FLOAT32, count=1),
    ]

    msg = PointCloud2()
    msg.header = Header()
    msg.header.frame_id = frame_id
    msg.height = 1
    msg.width  = n
    msg.fields = fields
    msg.is_bigendian = False
    msg.point_step   = 16          # 4 fields x 4 bytes
    msg.row_step     = 16 * n
    msg.is_dense     = True
    msg.data         = xyzrgb.astype(np.float32).tobytes()
    return msg


class PcdPublisher(Node):

    def __init__(self, cloud_msg: PointCloud2):
        super().__init__('pcd_publisher')
        self._msg = cloud_msg

        # Latched QoS — new RViz subscribers get the map immediately
        qos = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE,
        )
        self._pub = self.create_publisher(PointCloud2, PUBLISH_TOPIC, qos)
        self.create_timer(1.0 / PUBLISH_HZ, self._publish)
        self.get_logger().info(
            f'Publishing {self._msg.width:,} points on {PUBLISH_TOPIC}\n'
            f'  Frame  : {FRAME_ID}\n'
            f'  In RViz: Fixed Frame="{FRAME_ID}", '
            f'Add PointCloud2, topic={PUBLISH_TOPIC}, Color=RGB8'
        )

    def _publish(self):
        self._msg.header.stamp = self.get_clock().now().to_msg()
        self._pub.publish(self._msg)


def main():
    print(f'Reading {PCD_FILE} ...')
    xyzrgb = read_pcd_xyzrgb(PCD_FILE)
    print(f'Loaded {len(xyzrgb):,} points')

    cloud_msg = make_pointcloud2(xyzrgb, FRAME_ID)

    rclpy.init()
    node = PcdPublisher(cloud_msg)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()