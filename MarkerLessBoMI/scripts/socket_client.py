import socket

from matplotlib.pyplot import connect
from scripts.reaching import Reaching
import threading
import time

from scripts.reaching_functions import stop_thread

#HOST = "192.168.1.14"  # The server's hostname or IP address
#PORT = 8000  # The port used by the server

#with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
 #   s.connect((HOST, PORT))
  #  s.sendall(b"Hello, world")
  #  data = s.recv(1024)

#print(f"Received {data!r}")

#GLOBAL VARIABLES

bytes_to_send = None
send = False
close_connection = False
DISCONNECT_MESSAGE = "!DISCONNECT"
DISCONNECT_BYTES_MESSAGE = bytes(DISCONNECT_MESSAGE,'UTF-8')

#To take trace of the base teleoperation state
base_state = None

def parse_data(r):
    """
    This function parse data into bytes in order to be send by socket communication as byte format
    The attributes control_base and control_arn specifies if the user want to control arm or base
    """
    global bytes_to_send
    if r.control_base == True:
        #We have to send base commands
        string_data = "lin_vel:" + str(r.lin_vel) + " ang_vel:" + str(r.ang_vel)
    elif r.control_arm == True:
        #we have to send arm commands
        string_data = "joint1:" + str(.1) + " joint2:" + str(r.joint_state[1]) + " joint3:" + str(r.joint_state[2]) + \
        " joint4:" + str(r.joint_state[3]) + " joint5:" + str(r.joint_state[4]) + " joint6:" + str(r.joint_state[5]) + \
        " joint7:" + str(r.joint_state[6]) + " joint8:" + str(r.joint_state[7]) 

    bytes_data = bytes(string_data,'UTF-8')
    bytes_to_send =bytes_data
    return bytes_data



def parse_target_pos(x,y):
    """
    Simple function that parse a byte with the coordinates of the target position
    :param x: x coordinate of the target y: y coordinate of the target
    :return bytes_to_send: the formatted bytes to send to the server
    """
    global bytes_to_send
    string_data = "x:" + str(x) + " y:" + str(y)
    bytes_to_send = bytes(string_data,'UTF-8')
    return bytes_to_send

def parse_bash_file(FORMAT):
    """
    Simple function that parse a string to be send in order to execute the wanted bash file on UBUNTU
    :param FORMAT: string that specify the wanted bash file
    :return bytes_to_send: the formatted bytes to send to the server
    """
    global bytes_to_send
    string_to_send = FORMAT
    bytes_to_send = bytes(string_to_send,'UTF-8')
    return bytes_to_send
    

def send_data(bytes_data):
    """
    Function to send the bytes data in the socket communication
    """
    global send
    send = True
    
def manage_connection_server(connection):
    """
    Function used to connect with server
    """
    global close_connection
    if connection:
        close_connection = False
        print("[CONNECTION] Client is connecting to server...")
        thread = threading.Thread(target=client_connected,args=[connection])
        thread.start()
    else:
        print("[CONNECTION] Client want to close connection")
        close_connection = True

def set_base_teleop_state(base_teleop_state):
    """
    This function simply change the base teleop state in order to send the value 
    to the socket server in order to keep track of the base teleoperation state
    base_teleop_state == True --> 'nine region GUI'
    base_teleop_state == False --> 'odom GUI
    """
    global base_state,bytes_to_send
    base_state = base_teleop_state
    if base_state == True:
        bytes_to_send = bytes("nine region",'UTF-8')
    elif base_state == False:
        bytes_to_send = bytes("odom",'UTF-8')
    return bytes_to_send



def client_connected(connection):
    global send,bytes_to_send,close_connection
    HOST = "192.168.5.27"  # The server's hostname or IP address
    #HOST = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    PORT = 5051 # The port used by the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("[CLIENT] Connected!!")
        while True:
            if send:
                s.sendall(bytes_to_send)
                send = False
            if close_connection:
                #send disconnect message
                s.sendall(DISCONNECT_BYTES_MESSAGE)
                break    
            time.sleep(0.001)
            
