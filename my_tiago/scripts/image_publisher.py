#!/usr/bin/env python

# from glob import escape
# from operator import imod
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
from sensor_msgs.msg import Image,CompressedImage

#OpenCV
import cv2
from cv_bridge import CvBridge

import numpy as np

class send_image_socket():
    FORMAT = "utf-8"
    DISCONNECT_MESSAGE = "!DISCONNECT"
    def __init__(self,ip_server,port):
        rospy.init_node("image_publisher")
        self.PORT = port
        self.SERVER_IP = ip_server
        self.ADDR = (self.SERVER_IP,self.PORT)
        self.img_sub = rospy.Subscriber("xtion/rgb/image_raw",Image, self.send_img_processed, queue_size=1)
        #self.img_sub = rospy.Subscriber("/processed_image/republish",CompressedImage, self.send_img_processed, queue_size=1)
        self.FORMAT = "utf-8"


    def send_img_processed(self,msg):
        cv_br = CvBridge()
        cv2_img = cv_br.imgmsg_to_cv2(msg,"bgr8")
        
        #####Process data in order to send it into socket communication#########
        encode_param =[int(cv2.IMWRITE_JPEG_QUALITY),90]
        result,imgencode = cv2.imencode('.jpg',cv2_img,encode_param)
        data = np.array(imgencode)
        stringData = data.tostring()
        #####################################################################

        decimg = cv2.imdecode(data,1)
        #cv2.imshow("TIAGO HEAD Client",decimg)
        #cv2.waitKey(0)
        client = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM) 
        client.connect(self.ADDR)
        try:
            client.send(str(len(stringData)).ljust(16))
            client.send(stringData)
            print("Message correctly send")
        except:
            print("Impossible to send image message")
        client.close()

if __name__ == "__main__":
    ip_add = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    #ip_add = "192.168.1.14"
    print("Client IP:" + str(ip_add))
    port = 8085
    client = send_image_socket(ip_add,port)
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting Down")

