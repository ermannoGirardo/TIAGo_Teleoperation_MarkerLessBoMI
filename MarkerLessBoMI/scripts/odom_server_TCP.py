#!/usr/bin/env python3

import socket



FORMAT = "utf-8"

def server_sub(addr,backlog=1):
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
        data = conn.recv(1024).decode(FORMAT) 
        print("Message Received:"+ str(data))
        if not data:
            conn.close()


if __name__ == "__main__":
    '''
    Initialize the node
    '''
    ip_add = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    print("[SERVER] Initialize the server on:"+ip_add)
    server_sub((ip_add,8080))
     
