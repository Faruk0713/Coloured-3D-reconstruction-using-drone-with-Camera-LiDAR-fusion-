#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
import sys
import tty
import termios

MSG = """
--------------------------
   Recon Drone Teleop
--------------------------
  T      : Takeoff
  L      : Land
  W / S  : Forward / Backward
  A / D  : Turn Left / Right
  U / J  : Move Up / Down
  Q / E  : Strafe Left / Right
  X      : Stop / Hover
  K      : Kill (Emergency Stop)
  Ctrl+C : Quit
--------------------------
"""

def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

class TeleopReconDrone(Node):
    def __init__(self):
        super().__init__('teleop_recon_drone')

        self.pub_vel      = self.create_publisher(Twist, '/recon_drone/cmd_vel', 10)
        self.pub_takeoff  = self.create_publisher(Empty, '/recon_drone/takeoff', 10)
        self.pub_land     = self.create_publisher(Empty, '/recon_drone/land', 10)
        self.pub_reset    = self.create_publisher(Empty, '/recon_drone/reset', 10)

        self.linear_speed  = 1.0
        self.angular_speed = 1.0
        self.vertical_speed = 0.5
        self.strafe_speed  = 0.5

    def run(self):
        settings = termios.tcgetattr(sys.stdin)
        print(MSG)
        try:
            while True:
                key = get_key(settings)
                twist = Twist()

                if key == 't':
                    self.pub_takeoff.publish(Empty())
                    self.get_logger().info('Takeoff!')

                elif key == 'l':
                    self.pub_land.publish(Empty())
                    self.get_logger().info('Landing!')

                elif key == 'k':
                    self.pub_reset.publish(Empty())
                    self.get_logger().info('Emergency Stop!')

                elif key == 'w':
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

                elif key == 'q':
                    twist.linear.y = self.strafe_speed

                elif key == 'e':
                    twist.linear.y = -self.strafe_speed

                elif key == 'x':
                    pass  # all zeros = hover/stop

                elif key == '\x03':  # Ctrl+C
                    print("Quitting...")
                    break

                self.pub_vel.publish(twist)

        finally:
            # Make sure drone hovers on exit
            self.pub_vel.publish(Twist())
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

def main():
    rclpy.init()
    node = TeleopReconDrone()
    node.run()
    rclpy.shutdown()

if __name__ == '__main__':
    main()