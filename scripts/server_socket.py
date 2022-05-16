import socket 
import threading
import numpy as np

HEADER = 64
PORT = 5050
SERVER = "192.168.56.1"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
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
    joints = np.zeros(8)
    #check for lin_vel
    if 'lin_vel:' in msg:
        position = msg.find('lin_vel:')
        float_pos = position + len("lin_vel:")
        if msg[float_pos] == '-':
            lin_vel =msg[float_pos:float_pos + 4]
        else:
            lin_vel = msg[float_pos: float_pos + 3]
    #check for ang_vel
    if 'ang_vel:' in msg:
        position = msg.find('ang_vel:')
        float_pos = position + len("ang_vel:")
        if msg[float_pos] == '-':
            lin_vel = msg[float_pos:float_pos + 4]
        else:
            ang_vel = msg[float_pos: float_pos + 3]
    #check for joint1
    if 'joint1:' in msg:
        position = msg.find('joint1:')
        float_pos = position + len("joint1:")
        float_value =  float(msg[float_pos: float_pos + 3])
        joints[0] = float_value
    #check for joint2
    if 'joint2:' in msg:
        position = msg.find('joint2:')
        float_pos = position + len("joint2:")
        float_value = msg[float_pos: float_pos + 4]
        joints[1] = float_value
    #check for joint3
    if 'joint3:' in msg:
        position = msg.find('joint3:')
        float_pos = position + len("joint3:")
        float_value = msg[float_pos: float_pos + 3]
        joints[2] = float_value
    #check for joint4
    if 'joint4:' in msg:
        position = msg.find('joint4:')
        float_pos = position + len("joint4:")
        float_value = msg[float_pos: float_pos + 3]
        joints[3] = float_value
    #check for joint5
    if 'joint5:' in msg:
        position = msg.find('joint5:')
        float_pos = position + len("joint5:")
        float_value = msg[float_pos: float_pos + 3]
        joints[4] = float_value
    #check for joint6
    if 'joint6:' in msg:
        position = msg.find('joint6:')
        float_pos = position + len("joint6:")
        float_value = msg[float_pos: float_pos + 3]
        joints[5] = float_value
    #check for joint7
    if 'joint7:' in msg:
        position = msg.find('joint7:')
        float_pos = position + len("joint7:")
        float_value = msg[float_pos: float_pos + 3]
        joints[6] = float_value
    #check for joint8
    if 'joint8:' in msg:
        position = msg.find('joint8:')
        float_pos = position + len("joint8:")
        float_value = msg[float_pos: float_pos + 3]
        joints[7] = float_value

    print('Joints values is:' + str(joints))


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:     
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()



