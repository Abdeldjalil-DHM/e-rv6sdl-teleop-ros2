#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from ultralytics import YOLO
import cv2
import json
import base64

class YOLODetectionNode(Node):
    def __init__(self):
        super().__init__('yolo_detection_node')
        
        self.get_logger().info('🎯 Loading YOLOv8n...')
        self.model = YOLO('yolov8n.pt')
        self.get_logger().info('✅ YOLOv8n Loaded!')
        
        self.cap = cv2.VideoCapture(0)
        self.pub_image = self.create_publisher(String, '/yolo/annotated_image', 10)
        self.pub_detections = self.create_publisher(String, '/yolo/detections', 10)
        self.timer = self.create_timer(0.05, self.yolo_callback)
        self.frame_count = 0
    
    def yolo_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        
        self.frame_count += 1
        
        try:
            results = self.model(frame, verbose=False, conf=0.45)
            annotated_frame = results[0].plot()
            
            _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            img_msg = String()
            img_msg.data = img_base64
            self.pub_image.publish(img_msg)
            
            boxes = results[0].boxes
            detections = []
            
            for box in boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(box.conf[0])
                
                detections.append({
                    'class': class_name,
                    'confidence': round(confidence, 3)
                })
            
            det_msg = String()
            det_msg.data = json.dumps(detections)
            self.pub_detections.publish(det_msg)
            
            if self.frame_count % 60 == 0:
                self.get_logger().info(f'📊 {len(detections)} objects detected')
        
        except Exception as e:
            self.get_logger().error(f'❌ Error: {e}')
    
    def destroy_node(self):
        self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = YOLODetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
