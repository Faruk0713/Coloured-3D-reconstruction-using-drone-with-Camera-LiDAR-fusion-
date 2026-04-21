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
  ── Speed Controls ───────
  Z / C  : Linear  speed  -/+
  B / N  : Angular speed  -/+
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
        self.pub_vel     = self.create_publisher(Twist, '/recon_drone/cmd_vel', 10)
        self.pub_takeoff = self.create_publisher(Empty, '/recon_drone/takeoff', 10)
        self.pub_land    = self.create_publisher(Empty, '/recon_drone/land', 10)
        self.pub_reset   = self.create_publisher(Empty, '/recon_drone/reset', 10)

        self.linear_speed   = 1.0
        self.angular_speed  = 1.0
        self.vertical_speed = 0.5
        self.strafe_speed   = 0.5

        # Speed adjustment step and limits
        self._lin_step  = 0.1
        self._ang_step  = 0.1
        self._lin_min,  self._lin_max  = 0.1, 3.0
        self._ang_min,  self._ang_max  = 0.1, 2.0

    def _print_speeds(self):
        print(f'\r  [Speed]  linear={self.linear_speed:.1f}  '
              f'angular={self.angular_speed:.1f}  '
              f'vertical={self.vertical_speed:.1f}  '
              f'strafe={self.strafe_speed:.1f}        ', flush=True)

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

                # ── Movement ──────────────────────────────────────────
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

                # ── Speed controls ────────────────────────────────────
                elif key == 'z':
                    self.linear_speed   = round(max(self._lin_min, self.linear_speed  - self._lin_step), 1)
                    self.vertical_speed = round(max(self._lin_min, self.vertical_speed - self._lin_step), 1)
                    self.strafe_speed   = round(max(self._lin_min, self.strafe_speed  - self._lin_step), 1)
                    self._print_speeds()
                elif key == 'c':
                    self.linear_speed   = round(min(self._lin_max, self.linear_speed  + self._lin_step), 1)
                    self.vertical_speed = round(min(self._lin_max, self.vertical_speed + self._lin_step), 1)
                    self.strafe_speed   = round(min(self._lin_max, self.strafe_speed  + self._lin_step), 1)
                    self._print_speeds()
                elif key == 'b':
                    self.angular_speed = round(max(self._ang_min, self.angular_speed - self._ang_step), 1)
                    self._print_speeds()
                elif key == 'n':
                    self.angular_speed = round(min(self._ang_max, self.angular_speed + self._ang_step), 1)
                    self._print_speeds()

                elif key == '\x03':  # Ctrl+C
                    print("\nQuitting...")
                    break

                self.pub_vel.publish(twist)

        finally:
            self.pub_vel.publish(Twist())
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

def main():
    rclpy.init()
    node = TeleopReconDrone()
    node.run()
    rclpy.shutdown()

if __name__ == '__main__':
    main()