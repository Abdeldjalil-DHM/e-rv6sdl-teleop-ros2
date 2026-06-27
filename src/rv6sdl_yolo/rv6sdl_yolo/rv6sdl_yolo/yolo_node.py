#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose
from vision_msgs.msg import BoundingBox2D
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO
import numpy as np

class YoloIndustryNode(Node):
    def __init__(self):
        super().__init__('rv6sdl_yolo')
        self.get_logger().info('🚀 RV6SDL YOLO Industry Node started!')
        
        # Load YOLO model (industry/safety optimized)
        self.model = YOLO('yolov8n.pt')
        self.bridge = CvBridge()
        
        # Subscribers/Publishers
        self.sub_img = self.create_subscription(
            Image, '/image_raw', self.image_callback, 10)
        self.pub_dets = self.create_publisher(Detection2DArray, '/yolo_detections', 10)
        self.pub_img = self.create_publisher(Image, '/yolo_image', 10)
        
        self.get_logger().info('Waiting for /image_raw...')

    def image_callback(self, msg):
        try:
            # Convert ROS -> OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # YOLO inference
            results = self.model(cv_image, verbose=False, conf=0.5)
            
            # Prepare detections message
            dets_msg = Detection2DArray()
            dets_msg.header = msg.header
            
            # Annotated image
            annotated = results[0].plot()
            
            # Parse detections
            for r in results[0].boxes:
                det = Detection2D()
                det.bbox = BoundingBox2D()
                
                # Bounding box
                x1, y1, x2, y2 = r.xyxy[0].cpu().numpy()
                det.bbox.center.x = (x1 + x2) / 2
                det.bbox.center.y = (y1 + y2) / 2
                det.bbox.size_x = x2 - x1
                det.bbox.size_y = y2 - y1
                
                # Class + confidence
                cls_id = int(r.cls[0])
                conf = float(r.conf[0])
                class_name = self.model.names[cls_id]
                
                hyp = ObjectHypothesisWithPose()
                hyp.id = cls_id
                hyp.score = conf
                hyp.hypothesis_class = class_name
                det.results.append(hyp)
                
                dets_msg.detections.append(det)
            
            # Publish
            self.pub_dets.publish(dets_msg)
            self.pub_img.publish(self.bridge.cv2_to_imgmsg(annotated, encoding='bgr8'))
            
            if len(dets_msg.detections) > 0:
                self.get_logger().info(f'🎯 Detected: {[d.results[0].hypothesis_class for d in dets_msg.detections]}')
                
        except Exception as e:
            self.get_logger().error(f'Error: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    node = YoloIndustryNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
