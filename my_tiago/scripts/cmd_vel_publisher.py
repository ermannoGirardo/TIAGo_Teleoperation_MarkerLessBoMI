#! /usr/bin/env python3

#ROS LIBRARIES

from re import T
import rospy
from geometry_msgs.msg import Twist,Point
from nav_msgs.msg import *
from move_base_msgs.msg import *
from std_msgs.msg import *

#STD PYTHON LIBRARIES
import actionlib
import math
import time
import os

#GLOBAL VARIABLES

CONSTANT_RAW1 = "lin_vel"
CONSTANT_RAW2 = "ang_vel"
CONSTANT_RAW3 = "x_coor"
CONSTANT_RAW4 = "y_coor"
CONSTANT_RAW5 = "base_state"
CONSTANT_RAW6 = "map_name"


my_hash_table = [CONSTANT_RAW1,CONSTANT_RAW2,CONSTANT_RAW3,CONSTANT_RAW4,CONSTANT_RAW5,CONSTANT_RAW6]
path = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "../FILES/data.txt"
abs_file_path = os.path.join(path, rel_path)


my_settings_file = open(abs_file_path, "r+")


cannot_read_counter = 0

tiago_position = Point()


## COMPUTE THE MAP REGION
x_min = None
x_max = None
y_min = None
y_max = None


#FUNCTIONS

def read_value(what,matrix):
    """
    Function used to read a value into data.txt file
    :param
        what: MACRO belongs to my_hash_table
        matrix: the extracted matrix from the file

    :return_value:
        wanted_value: value [string] that the user wants to read
    """
    counter = 0
    global cannot_read_counter, my_hash_table
    for item in my_hash_table:
        if what == item:
            break
        counter  = counter + 1
    #if the flag value is '1' the reader can read
    if matrix[counter][1] == '1':
        wanted_value = matrix[counter][0] 
    
    #if the value is not readable
    else:
        print("I cannot read, writer is modifing the variable!")

        #default value for base_state
        if (what == 'base_state') or (what == 'x_coor') or (what == 'y_coor') or (what == 'map_name'):
            cannot_read_counter = cannot_read_counter + 1
            wanted_value = 'None'

        #default value for other item is 0
        else:
            cannot_read_counter = cannot_read_counter + 1
            wanted_value = '+0.0'
    return wanted_value


def scompose_raws_into_matrix(list_of_lines):
    """
    Function used to compose the matrix from the list of lines
    :param
        list_of_lines: the array of the file's lines
    :return 
        matrix: the composed matrix
    """
    raw1 = list_of_lines[0].split()
    raw2 = list_of_lines[1].split()
    raw3 = list_of_lines[2].split()
    raw4 = list_of_lines[3].split()
    raw5 = list_of_lines[4].split()
    raw6 = list_of_lines[5].split()
    matrix =  [raw1,raw2,raw3,raw4,raw5,raw6]
    return matrix

def odom_clbk(odom_msg):
    """
    Simple odom callback that update TIAGo position into a global variable
    :param 
        odom_msg: the odom msg from subcriber
    """
    global tiago_position
    tiago_position = odom_msg.pose.pose.position
    #print("TIAGo position: x: " + str(tiago_position.x) + " y: " + str(tiago_position.y))

def euler_dist(point1,point2):
    """
    Simple function that computes the euler distance between two 2D points
    :params
        point1: first of the two points
        point2: second of the two points
    """
    dist = math.sqrt((point2.x - point1.x)**2 + (point2.y - point1.y)**2)
    return dist

def check_valid_coordinate(x_coor,y_coor):
    """
    Simple function that computes if the selected coordinates are valid or not
    Of course they depend on TIAGo position, since taret = TIAGo_pos + selected target
    :params
        x_coor: the x coordinate of the target
        y_coor: the y coordinate of the target
    :return
        flag [bool]: True if the coordinates are valid, False otherwise
    """
    global x_min,x_max,y_min,y_max
    if (x_coor  <= x_max) and (x_coor >= x_min):
        if (y_coor  <= y_max) and (y_coor >= y_min):
            flag = True
        else:
            flag = False
    else:
        flag = False
    return flag


def move_tiago():
    """
    Function used to move TIAGo
    If FSM state is to teleoperate the base with 'nine regions gui':
        it publishes on the topic /mobile_base_controller/cmd_vel the values taken from /FILES/data.txt
    The value into data.txt are modified runtime by server_socket.py 
    If FSM state is to teleoperate the base with ' odom gui':  
        Once the values (x_coor and y_coor) from the server are modified, it publish on the topic /move_base_simple/goal 
        a new target to be reached by TIAGo
    """
    global tiago_position,my_settings_file
    global x_min,x_max,y_min,y_max

    # Starts a new node
    print("Cmd Vel publisher node [STARTED]")
    rospy.init_node('cmd_vel_publisher', anonymous=True)
    
    #Declare a publisher on the topic /mobile_base_controller/cmd_vel
    cmd_vel_publisher = rospy.Publisher('/mobile_base_controller/cmd_vel', Twist, queue_size=10)

    #Declare a subscriber on /mobile_base_controller/odom
    odom_sub = rospy.Subscriber('/mobile_base_controller/odom',Odometry,odom_clbk)
    
    #Declare a client on the topic /move_base_simple/goal 
    move_base_client = actionlib.SimpleActionClient('move_base', move_base_msgs.msg.MoveBaseAction)
    
    #Declare a twist msg
    vel_msg = Twist()
    
    #Declare a rate of 10 Hz
    rate = rospy.Rate(10) # 10hz

    counter_seq = 0

    #read the file
    #and extract information about map size
    my_settings_file.seek(0,0)
    list_of_lines = my_settings_file.readlines()
    matrix = scompose_raws_into_matrix(list_of_lines)

    #extract the map size
    map_name = read_value("map_name", matrix)

    #Variable to store the information about the first goal
    #Used to understand if it is necessary to cancel the goal
    first_goal = True

    #until the value is not readable
    while map_name == 'None':

        #first read the state of the base
        #read the file
        my_settings_file.seek(0,0)
        list_of_lines = my_settings_file.readlines()
        matrix = scompose_raws_into_matrix(list_of_lines)

        #extract the base state value 
        wanted_value = read_value("map_name", matrix)

    #Once extract the name of the map update the min and max values

    if map_name == 'map1':
        x_min = -4.35
        x_max = 4.35
        y_min = -12.36
        y_max = 1.32
    
    elif map_name == 'map2':
        x_min = -4.25
        x_max = 4.25
        y_min = -4.2
        y_max = 9.3

    
    #Main loop
    while not rospy.is_shutdown():
        
        #Avoid that base_state is not readable
        #first read the state of the base
        #read the file
        my_settings_file.seek(0,0)
        list_of_lines = my_settings_file.readlines()
        matrix = scompose_raws_into_matrix(list_of_lines)

        #extract the base state value 
        wanted_value = read_value("base_state", matrix)

        #until the value is not readable
        while wanted_value == 'None':

            #first read the state of the base
            #read the file
            my_settings_file.seek(0,0)
            list_of_lines = my_settings_file.readlines()
            matrix = scompose_raws_into_matrix(list_of_lines)

            #extract the base state value 
            wanted_value = read_value("base_state", matrix)
        
        #Convert to float
        base_state = float(wanted_value)

        #if the value == 1.0 --> nine region GUI
        #move TIAGo thanks cmd_vel values
        if base_state == 1.0:
            #read the file
            my_settings_file.seek(0,0)
            list_of_lines = my_settings_file.readlines()
            matrix = scompose_raws_into_matrix(list_of_lines)
            #extract the linear vel 
            wanted_value = read_value("lin_vel", matrix)
            lin_vel = float(wanted_value)
            #read the file
            my_settings_file.seek(0,0)
            list_of_lines = my_settings_file.readlines()
            matrix = scompose_raws_into_matrix(list_of_lines)
            #extract the angular vel
            wanted_value = read_value("ang_vel", matrix)
            ang_vel = float(wanted_value)

            print("Ho letto a 10 Hz i seguenti valori: " + str(lin_vel) + " " + str(ang_vel))

            vel_msg.linear.x = lin_vel
            vel_msg.angular.z = ang_vel

            cmd_vel_publisher.publish(vel_msg)

        #if odom GUI is stated
        if base_state == 0.0:
            #read value of x_coor and y_coor

            #read the file
            my_settings_file.seek(0,0)
            list_of_lines = my_settings_file.readlines()
            matrix = scompose_raws_into_matrix(list_of_lines)
            #extract the x_coordinate
            wanted_x_coordinate = read_value("x_coor", matrix)
            
            #read the file
            my_settings_file.seek(0,0)
            list_of_lines = my_settings_file.readlines()
            matrix = scompose_raws_into_matrix(list_of_lines)
            #extract the y_coordinate
            wanted_y_coordinate = read_value("y_coor", matrix)

            #if they are already not Null
            if wanted_x_coordinate != 'None':
                x_coor = float(wanted_x_coordinate)
                print("You have selected x: " + str(x_coor))

            if wanted_y_coordinate !='None':
                y_coor = float(wanted_y_coordinate)
                print("You have selected y: " + str(y_coor))
                
            #The values for x and y coor has to be changed to send a position
            #Until x_coor or y_coor == 'None' continue to read values until both has been changed
            while (wanted_x_coordinate == 'None') or (wanted_y_coordinate == 'None'):
                #read value of x_coor and y_coor

                #read the file
                my_settings_file.seek(0,0)
                list_of_lines = my_settings_file.readlines()
                matrix = scompose_raws_into_matrix(list_of_lines)
                #extract the x_coordinate
                wanted_x_coordinate = read_value("x_coor", matrix)
                if wanted_x_coordinate != 'None':
                    x_coor = float(wanted_x_coordinate)
                
                #read the file
                my_settings_file.seek(0,0)
                list_of_lines = my_settings_file.readlines()
                matrix = scompose_raws_into_matrix(list_of_lines)
                #extract the y_coordinate
                wanted_y_coordinate = read_value("y_coor", matrix)
                if wanted_y_coordinate !='None':
                    y_coor = float(wanted_y_coordinate)

            #Now I am sure that values has been initialized
            #First stop the robot 
            print("You have selected x: " + str(x_coor) + " y: " + str(y_coor))

            #If it is not the first goal
            #Cancel all the goals
            if first_goal == False:
                move_base_client.cancel_all_goals()

            stop_msg = Twist()
            stop_msg.linear.x = 0
            stop_msg.angular.z = 0
            cmd_vel_publisher.publish(stop_msg)
            time.sleep(.5)

            #Declare the target position
            target_position = Point()
            target_position.x = x_coor + tiago_position.x
            target_position.y = y_coor + tiago_position.y

            #check if the target position is valid
            #if yes then publish as goal with MoveBase
            
            flag = check_valid_coordinate(target_position.x,target_position.y)
            if flag == True:

                print("The selected coordinates are valid!")

                #wait the server and send the goal
                move_base_client.wait_for_server()
                print("Waiting Move Base Server...")

                #Declare and fill a move base goal
                target_pos = move_base_msgs.msg.MoveBaseActionGoal()
                target_pos.goal.target_pose.header.frame_id = 'map'
                time_now = rospy.Time.now()
                target_pos.goal.target_pose.header.seq = counter_seq
                counter_seq = counter_seq + 1
                # target_pos.goal.target_pose.header.stamp.secs = time_now.secs
                # target_pos.goal.target_pose.header.stamp.nsecs = time_now.nsecs
                target_pos.goal.target_pose.header.stamp = rospy.Time.now()
                target_pos.goal.target_pose.pose.position.x = target_position.x
                target_pos.goal.target_pose.pose.position.y = target_position.y
                target_pos.goal.target_pose.pose.orientation.w = 1 #default orientation


                move_base_client.send_goal(target_pos.goal)
                first_goal = False
                print("Goal position sended")
                # wait = move_base_client.wait_for_result()
                # if not wait:
                #     rospy.logerr("Action server not available!")
                #     rospy.signal_shutdown("Action server not available!")
                # else:
                #     print("TIAGo is arrived in x: " + str(target_position.x) + " y: " + str(target_position.y))


            ################################################################

            else:
                print("Target out of the map!")

            #Restore the values for x_coor and y_coor to None
            #First restore x_coor
            #Restore the flag
            #Move the object pointer to the location flag
            my_settings_file.seek(19,0)

            #modify the flag on file
            my_settings_file.write('0')
            my_settings_file.flush()

            #Change the value to None
            #Move the object pointer to the location flag
            my_settings_file.seek(14,0)

            #modify the flag on file
            my_settings_file.write('None')
            my_settings_file.flush()

            #Restore the flag to '1'
            #Move the object pointer to the location flag
            my_settings_file.seek(19,0)

            #modify the flag on file
            my_settings_file.write('1')
            my_settings_file.flush()

            #Restore the value for y_coor

            #Restore the flag
            #Move the object pointer to the location flag
            my_settings_file.seek(26,0)

            #modify the flag on file
            my_settings_file.write('0')
            my_settings_file.flush()

            #Change the value to None
            #Move the object pointer to the location flag
            my_settings_file.seek(21,0)

            #modify the flag on file
            my_settings_file.write('None')
            my_settings_file.flush()

            #Restore the flag to '1'
            #Move the object pointer to the location flag
            my_settings_file.seek(26,0)

            #modify the flag on file
            my_settings_file.write('1')
            my_settings_file.flush()

            ###########################################################

        rate.sleep()


if __name__ == '__main__':
    """
    Entry point of the script
    It call the function move_tiago until an interrupt exception by the user is given (Ctrl + c)
    """
    try:
        move_tiago()
    except rospy.ROSInterruptException: 
        pass