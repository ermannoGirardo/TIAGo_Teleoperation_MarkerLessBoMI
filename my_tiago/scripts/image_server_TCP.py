#!/usr/bin/env python

import socket
import cv2
from cv_bridge import CvBridge
import os
import numpy as np

FORMAT = "utf-8"
path = os.path.dirname(os.path.abspath(__file__)) + "\\..\\TestFile.txt"
image_file = open(path,"w+")
#WINDOW_NAME = "TIAGo Head Camera"


def recvall(sock,count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def server_sub(addr,backlog=1):
    global WINDOW_NAME
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.bind(addr)
        s.listen(backlog)
        print("[SERVER] Listening on:" + str(addr))
    except socket.error as error:
        print("[SERVER] Does not response")
        print("Try to restart the server")
        server_sub(addr,backlog=1)


    while True:
        conn,client_addr = s.accept()
        length = recvall(conn,16)
        stringData = recvall(conn,int(length))
        data = np.fromstring(stringData,dtype='uint8')

        decimg = cv2.imdecode(data,1)
        #cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)        # Create window with freedom of dimensions
        # cv2.resizeWindow(WINDOW_NAME, 1800, 900)
        cv2.imshow("TIAGo Head Camera",decimg)
        cv2.waitKey(15)


if __name__ == "__main__":
    '''
    Initialize the node
    '''
    ip_add = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    print("[SERVER] Initialize the server on:"+ip_add)
    server_sub((ip_add,8085))
     
