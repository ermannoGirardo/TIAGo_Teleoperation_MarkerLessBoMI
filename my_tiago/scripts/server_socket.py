from lib2to3.pytree import Base
from pickle import TRUE
from re import X
import socket 
import threading
import numpy as np
import os
# import settings
from queue import Queue



# ROS
import rospy
from geometry_msgs.msg import *
from std_msgs.msg import *
from nav_msgs.msg import *
from my_tiago.msg import server_velocities

#GLOBAL VARIABLES
HEADER = 64
PORT = 5051
SERVER = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

base_teleop_state = None
list_of_lines = None
matrix_file = None


#FOR MANAGE THE FILE

    #PUNTATORE TABELLA FLAG
        # riga 1 --> seek(5,0)
        # riga 2 --> seek(12,0)
        # riga 3 --> seek(19,0)
        # riga 4 --> seek(26,0)
        # riga 5 --> seek(33,0)

    #TABELLA POSIZIONI VALORI
        #riga 1 --> seek(0,0)
        #riga 2 --> seek(7,0)
        #riga 3 --> seek(14,0)
        #riga 4 --> seek(21,0)
        #riga 5 --> seek(28,0)

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


my_settings_file = open(abs_file_path,"w+")

## FUNCTIONS
    
def handle_client(conn, addr):
    global linear_vel
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg = conn.recv(1024).decode(FORMAT)
        decode_msg(msg)
        if msg == DISCONNECT_MESSAGE:
            connected = False

        print(f"[{addr}] {msg}")

    conn.close()
        



def decode_msg(msg):
    """
    Function used to decode the msg sent by the socket client
    :param
        msg: string received by client 
    """
    global base_teleop_state,my_settings_file,list_of_lines,matrix_file

    #check for lin_vel in msg
    if 'lin_vel:' in msg:
        position = msg.find('lin_vel:')
        float_pos = position + len("lin_vel:")
        if msg[float_pos] == '-':
            lin_vel =msg[float_pos:float_pos + 4]
            flag_negative = True
        else:
            lin_vel = msg[float_pos: float_pos + 3]
            flag_negative = False

        #compose the data in order to be written in the file
        if flag_negative==False:
            modify_value("lin_vel", '+' + str(lin_vel), matrix_file,my_settings_file)
        else:
            modify_value("lin_vel",str(lin_vel), matrix_file,my_settings_file)

    #check for ang_vel in msg
    if 'ang_vel:' in msg:
        position = msg.find('ang_vel:')
        float_pos = position + len("ang_vel:")
        if msg[float_pos] == '-':
            ang_vel = msg[float_pos:float_pos + 4]
            flag_negative= True
        else:
            ang_vel = msg[float_pos: float_pos + 3]
            flag_negative = False

        #compose the data in order to be written in the file
        if flag_negative==False:
            modify_value("ang_vel", '+' + str(ang_vel), matrix_file,my_settings_file)
        else:
            modify_value("ang_vel",str(ang_vel), matrix_file,my_settings_file)
        

    #check for target position for odom GUI
    if 'x:' in msg:
        position = msg.find('x:')
        int_pos = position + len('x:')
        if msg[int_pos] == '-':
            x_coo = msg[int_pos:int_pos + 2]
            flag_negative = True
        else:
            x_coo = msg[int_pos]
            flag_negative = False

        #compose the data in order to be written in the file
        #in the following format
        #+/-x.x 0/1

        if (flag_negative==False) and (x_coo != 9.9):
            modify_value("x_coor", '+' + str(x_coo) + ".0", matrix_file,my_settings_file)
        
        elif (flag_negative==False) and (x_coo == 9.9):
            modify_value("x_coor", '+' + str(x_coo), matrix_file,my_settings_file)
        
        #is negative
        else:
            modify_value("x_coor",str(x_coo) + ".0", matrix_file,my_settings_file)

    if 'y:' in msg:
        position = msg.find('y:')
        int_pos = position + len('y:')
        if msg[int_pos] == '-':
            y_coo = msg[int_pos:int_pos + 2]
            flag_negative = True
        else:
            y_coo = msg[int_pos]
            flag_negative = False

        #compose the data in order to be written in the file
        if flag_negative==False:
            modify_value("y_coor", '+' + str(y_coo) + ".0", matrix_file,my_settings_file)
        else:
            modify_value("y_coor",str(y_coo) + ".0", matrix_file,my_settings_file)

    #check for start simple office simulation

    if 'simple_office' == msg:
        # ---EXECUTE THE CORRESPONDING BASH FILE ---#
        os.system('./simple_office.sh')
        print("[STARTING ...] Simple Office")
        modify_value("map_name",'map1',matrix_file,my_settings_file)

    elif 'simple_office_with_people' == msg:
        # ---EXECUTE THE CORRESPONDING BASH FILE ---#
        os.system('./simple_office_with_people.sh')
        print("[STARTING ...] Simple Office With People")
        modify_value("map_name",'map2',matrix_file,my_settings_file)
        



    # ---CHECK AND UPDATE THE STATE OF THE BASE ---#
    # 'nine regions' --> +1.0
    # 'odom' --> +0.0
    
    if "nine region" in msg:
        #write in the file the base state value
        modify_value("base_state", '+1.0', matrix_file,my_settings_file)

    if "odom" in msg:
        #write in the file the base state value
        modify_value("base_state", '+0.0', matrix_file,my_settings_file)


def init_file():
    """
    Function used to initialize the file
    In particular it writes on file the values for:
        linear_val and its corresponding flag
        angular_vel and its corresponding flag
        x_coordinate and its corresponding flag
        y_coordinate and its corresponding flag
        base_state and its corresponding flag
        the name of the map and its corresponding flag
    """
    global my_settings_file,list_of_lines,matrix_file
    print("I am initializing the file:")
    my_settings_file.write('+0.0' + " " + str(1) + "\n")
    my_settings_file.write('+0.0' + " " + str(1) + "\n")
    my_settings_file.write('None' + " " + str(1) +  "\n")
    my_settings_file.write('None' + " " + str(1) + "\n")
    my_settings_file.write('+0.0' + " " + str(1) + "\n")
    my_settings_file.write('None' + " " + str(1) + '\n')
    my_settings_file.flush()
    my_settings_file.seek(0,0)
    list_of_lines = my_settings_file.readlines()
    matrix_file = scompose_raws_into_matrix(list_of_lines)
    print("File initialized!")


def modify_value(what, value,matrix,file):
    """
    Function used to modify the wanted value in the file
    In particual it takes the wanted item, the value, the matrix of the file and the file
    :param
        what: see my_hash_table
        value: the value to be written in the file
        matrix: the matrix of lines written in the file and its value and flag
        file: the name of the file
    """
    counter = 0
    #You can see flag location in the table 
    corresponding_location_flag = 5
    corresponding_location_value = 0
    for item in my_hash_table:
        if what == item:
            break
        counter  = counter + 1
        corresponding_location_flag = corresponding_location_flag + 7
        corresponding_location_value = corresponding_location_value + 7
    
    # Modify the flag before write
    matrix[counter][1] = '0'

    #move pointer to location of the corresponding flag
    file.seek(corresponding_location_flag,0)

    #modify the flag on file
    file.write('0')
    file.flush()

    # Modify value on matrix
    matrix[counter][0] = value
    
    #Move pointer position to the value
    file.seek(corresponding_location_value,0)
    
    #Write on file
    file.write(value)
    file.flush()

    #restore flag
    matrix[counter][1] = '1'

    #move pointer to location of the corresponding flag
    file.seek(corresponding_location_flag,0)

    #modify the flag on file
    file.write('1')
    file.flush()

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
   
 


if __name__ == '__main__':
    """
    Entry point of the script
    In particular it initialize the file used for manage the variables.
    It starts the server putting it in listening mode.
    Once the client is connected to the server it starts a thread for receive the messages from the client
    """

    init_file()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    print("[STARTING] server is starting...")
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:     
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        thread.join()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")





