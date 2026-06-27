#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

class HelloJazzy(Node):
    def __init__(self):
        super().__init__('hello_jazzy')
        self.i = 0
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.get_logger().info('🚀 Hello ROS 2 Jazzy Jalisco!')

    def timer_callback(self):
        self.i += 1
        self.get_logger().info(f'Mon compteur: {self.i}')

def main():
    rclpy.init()
    node = HelloJazzy()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
