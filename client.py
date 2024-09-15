import socket
import threading
from uuid import getnode as get_mac

hostname = socket.gethostname()
host     = socket.gethostbyname(hostname)
port     = 8000
mac_adress=get_mac()

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((host,port))
client_socket.send(str(mac_adress).encode())
print(client_socket)
def username_conformation():
    username=input("Username: ")
    client_socket.send(username.encode())
    conformation=client_socket.recv(1024).decode()
    if(conformation!="True"):
        print(conformation)
        username_conformation()
def msg():
    message = input()
    while message.lower().strip() != "quit":
        client_socket.send(message.encode())
        message = input()
    client_socket.close()
username_conformation()
msg_thread        = threading.Thread(target=msg)
msg_thread.daemon = True
msg_thread.start()

while True:
    data = client_socket.recv(1024).decode()
    print(data)