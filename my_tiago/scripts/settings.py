#!/usr/bin/env python
from queue import Queue
from sys import maxsize
#Little cheating using Queue with maxsize = 1 --> number 
#In order to be sheared between Threads
def init():
    global linear_vel 
    linear_vel = Queue(maxsize=25)
    # linear_vel = None
    global angular_vel
    # angular_vel = None
    angular_vel = Queue(maxsize=25)
    global base_teleop_state
    # base_teleop_state = None
    base_teleop_state = Queue(maxsize=25)
    global x_coordinate
    # x_coordinate = None
    x_coordinate = Queue(maxsize=25)
    global y_coordinate
    # y_coordinate = None
    y_coordinate = Queue(maxsize=25)