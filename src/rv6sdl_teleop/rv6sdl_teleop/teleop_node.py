import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Pose
from std_msgs.msg import String, Int32
import math
class TeleopNode(Node):
    def __init__(self):
        super().__init__('rv6sdl_teleop_node')
        self.joints=[0.0]*6; self.speed=50; self.enabled=False
        self.homed=False; self.moving=False; self.estop=False; self._last_status=''
        self.joint_limits=[
            (math.radians(-170),math.radians(170)),
            (math.radians(-92), math.radians(135)),
            (math.radians(-129),math.radians(166)),
            (math.radians(-160),math.radians(160)),
            (math.radians(-120),math.radians(120)),
            (math.radians(-360),math.radians(360))
        ]
        self.js_pub=self.create_publisher(JointState,'/joint_states',10)
        self.status_pub=self.create_publisher(String,'/robot_status',10)
        self.tcp_pub=self.create_publisher(Pose,'/tcp_pose',10)
        self.create_subscription(String,'/robot_command',self.cmd_cb,10)
        self.create_subscription(String,'/robot_jog',self.jog_cb,10)
        self.create_subscription(Int32,'/robot_speed',self.speed_cb,10)
        self.create_timer(0.1,self.publish_all)
        self.get_logger().info('✅ rv6sdl_teleop_node démarré !')
    def cmd_cb(self,msg):
        cmd=msg.data.lower().strip()
        if cmd=='enable': self.enabled=True; self.estop=False
        elif cmd=='disable': self.enabled=False; self.moving=False
        elif cmd=='estop': self.estop=True; self.enabled=False; self.moving=False
        elif cmd=='reset': self.estop=False; self.moving=False
        elif cmd=='home':
            if self.enabled and not self.estop:
                self.joints=[0.0]*6; self.homed=True; self.get_logger().info('🏠 HOME OK')
    def jog_cb(self,msg):
        if not self.enabled or self.estop:
            self.get_logger().warn('⚠️ Robot pas ENABLED ou E-STOP actif !'); return
        parts=msg.data.lower().strip().split(':')
        jog=parts[0]
        step=math.radians(float(parts[1]) if len(parts)>1 else 5.0)*(self.speed/100.0)
        for i,name in enumerate(['j1','j2','j3','j4','j5','j6']):
            lo,hi=self.joint_limits[i]
            if jog==f'{name}+':
                self.joints[i]=min(hi,self.joints[i]+step); self.moving=True
                self.get_logger().info(f'✅ JOG {name}+ → {math.degrees(self.joints[i]):.1f}°')
                return
            if jog==f'{name}-':
                self.joints[i]=max(lo,self.joints[i]-step); self.moving=True
                self.get_logger().info(f'✅ JOG {name}- → {math.degrees(self.joints[i]):.1f}°')
                return
        self.get_logger().warn(f'❓ JOG inconnu: {jog}')
    def speed_cb(self,msg): self.speed=max(1,min(100,msg.data))
    def publish_all(self):
        now=self.get_clock().now().to_msg()
        js=JointState(); js.header.stamp=now
        js.name=['joint1','joint2','joint3','joint4','joint5','joint6']
        js.position=[round(j,6) for j in self.joints]; js.velocity=[0.0]*6
        self.js_pub.publish(js)
        pose=Pose()
        pose.position.x=round(450.0+self.joints[0]*100,4)
        pose.position.y=round(self.joints[1]*100,4)
        pose.position.z=round(380.0+self.joints[2]*100,4)
        pose.orientation.x=round(self.joints[3],6)
        pose.orientation.y=round(self.joints[4],6)
        pose.orientation.z=round(self.joints[5],6)
        pose.orientation.w=1.0
        self.tcp_pub.publish(pose)
        flags=['POWER']
        if self.enabled: flags.append('ENABLED')
        if self.moving:  flags.append('MOVING')
        if self.estop:   flags.append('ESTOP')
        if self.homed:   flags.append('HOMED')
        s_str=' '.join(flags)
        if s_str!=self._last_status:
            s=String(); s.data=s_str; self.status_pub.publish(s); self._last_status=s_str
        self.moving=False
def main(args=None):
    rclpy.init(args=args); rclpy.spin(TeleopNode()); rclpy.shutdown()
if __name__=='__main__': main()
