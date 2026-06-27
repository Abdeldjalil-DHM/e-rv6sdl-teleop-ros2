#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32
import socket
import math

ROBOT_IP = "192.168.120.20"
ROBOT_PORT = 10001

class CR2DAMelfaTeleop(Node):
    def __init__(self):
        super().__init__('cr2da_teleop_node')
        self.sock = None
        self.speed = 50
        self.connect_robot()
        # Subscribers
        self.sub_cmd = self.create_subscription(
            String, '/robot_command', self.on_command, 10)
        self.sub_jog = self.create_subscription(
            String, '/robot_jog', self.on_jog, 10)
        self.sub_speed = self.create_subscription(
            Int32, '/robot_speed', self.on_speed, 10)
        self.timer = self.create_timer(0.2, self.read_robot_state)

    def connect_robot(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((ROBOT_IP, ROBOT_PORT))
            self.get_logger().info(f"✅ CONNECTÉ AU ROBOT {ROBOT_IP}:{ROBOT_PORT}")
        except Exception as e:
            self.get_logger().error(f"❌ ÉCHEC CONNECTION ROBOT : {e}")

    def send_melfa(self, cmd: str) -> str:
        if not self.sock:
            self.get_logger().warn("🚫 Socket fermée, tentative de reconnexion...")
            self.connect_robot()
            if not self.sock:
                return ""
        msg = f"1;1;{cmd}\r\n"
        try:
            self.sock.sendall(msg.encode('ascii'))
            response = self.sock.recv(1024).decode('ascii').strip()
            self.get_logger().info(f"✉️ MELFA → {cmd} | Réponse: {response}")
            return response
        except Exception as e:
            self.get_logger().error(f"⚠️ ÉRREUR SUR SOCKET : {e}")
            self.sock = None
            return ""

    def on_command(self, msg: String):
        cmd = msg.data.strip().upper()
        if cmd == "HOME":
            # Commande MELFA pour aller HOME (adaptée à ton robot)
            self.send_melfa("EXECPRG")  # ou commande HOME réelle du robot
        elif cmd == "STOP":
            self.send_melfa("STOP")
        elif cmd == "ENABLE":
            self.send_melfa("SRVON")   # ou commande ENABLE MELFA
        elif cmd == "DISABLE":
            self.send_melfa("SRVOFF")  # ou équivalent

    def on_jog(self, msg: String):
        jog = msg.data.strip()
        self.send_melfa(f"JOG {jog}")

    def on_speed(self, msg: Int32):
        speed = max(1, min(100, msg.data))
        self.send_melfa(f"OVRD={speed}")

    def read_robot_state(self):
        try:
            self.send_melfa("STATE")
            self.send_melfa("JPOSF")
            self.send_melfa("PPOSF")
        except Exception as e:
            self.get_logger().error(f"Erreur lecture état robot : {e}")

def main(args=None):
    rclpy.init(args=args)
    node = CR2DAMelfaTeleop()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
