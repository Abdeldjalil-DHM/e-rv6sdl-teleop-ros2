#!/usr/bin/env python3
import socket
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32


class CR2DABridgeNode(Node):
    def __init__(self):
        super().__init__('cr2da_bridge_node')

        self.host = '192.168.120.20'
        self.port = 10001
        self.timeout = 2.0
        self.sock = None
        self.connected = False
        self.current_speed = 10

        self.status_pub = self.create_publisher(String, '/robot_status', 10)
        self.diag_pub = self.create_publisher(String, '/robot_diag', 10)

        self.create_subscription(String, '/robot_command', self.on_command, 10)
        self.create_subscription(String, '/robot_jog', self.on_jog, 10)
        self.create_subscription(Int32, '/robot_speed', self.on_speed, 10)

        self.connect_socket()
        self.timer = self.create_timer(1.0, self.poll_robot)
        self.get_logger().info('CR2DA bridge node started')

    def publish_status(self, text):
        msg = String()
        msg.data = text
        self.status_pub.publish(msg)

    def publish_diag(self, text):
        msg = String()
        msg.data = text
        self.diag_pub.publish(msg)

    def connect_socket(self):
        try:
            if self.sock:
                try:
                    self.sock.close()
                except Exception:
                    pass
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            self.connected = True
            self.get_logger().info(f'Connected to {self.host}:{self.port}')
            self.publish_status(f'CONNECTED {self.host}:{self.port}')
        except Exception as e:
            self.connected = False
            self.sock = None
            self.get_logger().error(f'Connection failed: {e}')
            self.publish_status(f'DISCONNECTED {e}')

    def clean_response(self, resp):
        if isinstance(resp, bytes):
            resp = resp.decode('ascii', errors='ignore')
        resp = resp.replace('\x00', '').strip()
        if resp.startswith('Qe'):
            resp = resp[2:]
        return resp

    def send_melfa(self, cmd):
        if not self.connected or self.sock is None:
            self.connect_socket()
            if not self.connected:
                return f'ERR:NOT_CONNECTED:{cmd}'
        try:
            payload = (cmd + '\r\n').encode('ascii', errors='ignore')
            self.sock.sendall(payload)
            raw = self.sock.recv(4096)
            resp = self.clean_response(raw)
            self.get_logger().info(f'MELFA -> {cmd} | Response: {resp}')
            self.publish_diag(f'CMD={cmd} RESP={resp}')
            return resp if resp else 'OK_EMPTY'
        except Exception as e:
            self.get_logger().error(f'Socket error on {cmd}: {e}')
            self.connected = False
            try:
                if self.sock:
                    self.sock.close()
            except Exception:
                pass
            self.sock = None
            return f'ERR:SOCKET:{e}'

    def start_sequence(self):
        seq = ['RESET', f'OVRD={self.current_speed}', 'START']
        results = []
        for c in seq:
            results.append(f'{c}=>{self.send_melfa(c)}')
            time.sleep(0.2)
        return ' | '.join(results)

    def on_command(self, msg):
        cmd = msg.data.strip().upper()
        self.get_logger().info(f'ROS command received: {cmd}')

        if cmd == 'ARM':
            resp = self.start_sequence()
        elif cmd in ['STATE', 'JPOSF', 'PPOSF', 'STOP', 'RESET', 'START']:
            resp = self.send_melfa(cmd)
        elif cmd.startswith('OVRD='):
            resp = self.send_melfa(cmd)
        elif cmd.startswith('MOV ') or cmd.startswith('MVS '):
            resp = self.send_melfa(cmd)
        elif cmd == 'PING':
            resp = 'PONG'
        else:
            resp = f'UNKNOWN_COMMAND:{cmd}'
            self.get_logger().warn(f'Commande inconnue: {cmd}')

        out = String()
        out.data = f'CMD={cmd} | RESP={resp}'
        self.status_pub.publish(out)

    def on_jog(self, msg):
        cmd = msg.data.strip().upper()
        self.get_logger().info(f'ROS jog received: {cmd}')

        if cmd in ['J1+', 'J1-', 'J2+', 'J2-', 'J3+', 'J3-', 'J4+', 'J4-', 'J5+', 'J5-', 'J6+', 'J6-']:
            resp = self.send_melfa(cmd)
        elif cmd.startswith('MOV ') or cmd.startswith('MVS '):
            resp = self.send_melfa(cmd)
        else:
            resp = f'UNKNOWN_JOG:{cmd}'
            self.get_logger().warn(f'Jog inconnu: {cmd}')

        out = String()
        out.data = f'JOG={cmd} | RESP={resp}'
        self.status_pub.publish(out)

    def on_speed(self, msg):
        self.current_speed = int(msg.data)
        self.get_logger().info(f'Speed set to {self.current_speed}')
        resp = self.send_melfa(f'OVRD={self.current_speed}')
        out = String()
        out.data = f'SPEED={self.current_speed} | RESP={resp}'
        self.status_pub.publish(out)

    def poll_robot(self):
        if not self.connected or self.sock is None:
            self.connect_socket()
            if not self.connected:
                return

        state = self.send_melfa('STATE')
        jposf = self.send_melfa('JPOSF')
        pposf = self.send_melfa('PPOSF')

        js = String()
        js.data = f'STATE={state};JPOSF={jposf}'
        self.status_pub.publish(js)

        tp = String()
        tp.data = f'PPOSF={pposf}'
        self.publish_diag(tp.data)

    def destroy_node(self):
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CR2DABridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
