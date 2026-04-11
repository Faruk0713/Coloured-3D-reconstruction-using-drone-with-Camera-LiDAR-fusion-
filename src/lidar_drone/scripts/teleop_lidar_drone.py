#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import tty
import termios

MSG = """
--------------------------
   LiDAR Drone Teleop
--------------------------
  W / S  : Forward / Backward
  A / D  : Turn Left / Right
  U / J  : Move Up / Down (Z)
  X      : Stop
  Q      : Quit
--------------------------
"""

def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

class TeleopLidarDrone(Node):
    def __init__(self):
        super().__init__('teleop_lidar_drone')
        self.pub = self.create_publisher(Twist, '/lidar_drone/cmd_vel', 10)
        self.linear_speed  = 1.0
        self.angular_speed = 1.0
        self.vertical_speed = 0.5

    def run(self):
        settings = termios.tcgetattr(sys.stdin)
        print(MSG)
        try:
            while True:
                key = get_key(settings)
                twist = Twist()

                if key == 'w':
                    twist.linear.x = self.linear_speed
                elif key == 's':
                    twist.linear.x = -self.linear_speed
                elif key == 'a':
                    twist.angular.z = self.angular_speed
                elif key == 'd':
                    twist.angular.z = -self.angular_speed
                elif key == 'u':
                    twist.linear.z = self.vertical_speed
                elif key == 'j':
                    twist.linear.z = -self.vertical_speed
                elif key == 'x':
                    pass  # stop
                elif key in ('q', '\x03'):
                    print("Quitting...")
                    break

                self.pub.publish(twist)

        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

def main():
    rclpy.init()
    node = TeleopLidarDrone()
    node.run()
    rclpy.shutdown()

if __name__ == '__main__':
    main()