#!/usr/bin/env python3

from glob import escape
import sys
import socket
import json
import time
import os
# ROS
import rospy
from geometry_msgs.msg import *
from std_msgs.msg import *
from nav_msgs.msg import *

class send_odom_socket():
    FORMAT = "utf-8"
    DISCONNECT_MESSAGE = "!DISCONNECT"
    def __init__(self,ip_server,port):
        rospy.init_node("send_tiago_position")
        self.PORT = port
        self.SERVER_IP = ip_server
        self.ADDR = (self.SERVER_IP,self.PORT)
        path = os.path.dirname(os.path.abspath(__file__))+"/odom_position.JSON"
        try:
            self.data_pos = json.load(open(path))
        except:
            print("I am not able to open JSON file")
        self.odom_sub = rospy.Subscriber("/mobile_base_controller/odom", Odometry, self.send_odom_pos, queue_size=1)


    def send_odom_pos(self,msg):
        self.data_pos["x"] = msg.pose.pose.position.x
        self.data_pos["y"] = msg.pose.pose.position.y
        msg = json.dumps(self.data_pos)
        client = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM) 
        client.connect(self.ADDR)
        message = msg.encode(self.FORMAT)
        try:
            client.send(message)
            print("Message correctly send")
        except:
            print("Impossible to send odom message")
        client.close()

if __name__ == "__main__":
    ip_add = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    print("Client IP:" + str(ip_add))
    port = 8080
    client = send_odom_socket(ip_add,port)
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting Down")

