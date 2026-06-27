import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from ultralytics import YOLO
import cv2, json, base64
import numpy as np
from sensor_msgs_py import set_image_from_numpy

class YoloNode(Node):
    def __init__(self):
        super().__init__('yolo_node')
        self.model = YOLO('yolo11n.pt')
        self.sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        self.det_pub = self.create_publisher(String, '/yolo/detections', 10)
        self.img_pub = self.create_publisher(String, '/yolo/annotated
