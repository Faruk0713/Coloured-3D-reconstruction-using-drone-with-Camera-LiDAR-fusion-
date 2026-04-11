#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import tty
import termios

MSG = """
--------------------------
    LiDAR Bot Teleop
--------------------------
  W   : Move Forward
  S   : Move Backward
  A   : Turn Left
  D   : Turn Right
  X   : Stop
  Q   : Quit
--------------------------
"""

def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

class TeleopBot(Node):
    def __init__(self):
        super().__init__('teleop_bot')
        self.pub = self.create_publisher(Twist, '/lidar_bot/cmd_vel', 10)
        self.linear_speed = 0.3
        self.angular_speed = 0.8

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
                elif key == 'x':
                    pass  # All zeros = stop
                elif key in ('q', '\x03'):
                    print("Quitting...")
                    break

                self.pub.publish(twist)

        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

def main():
    rclpy.init()
    node = TeleopBot()
    node.run()
    rclpy.shutdown()

if __name__ == '__main__':
    main()