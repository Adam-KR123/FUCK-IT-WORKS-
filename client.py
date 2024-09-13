import socket
import threading
import time

hostname=socket.gethostname()
host =socket.gethostbyname(hostname)
port = 8000

client_socket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((host,port))
print(client_socket)
def messaging():
    message=input()
    while message.lower().strip()!="quit":
        client_socket.send(message.encode())
        message=input()
    client_socket.close()

thread_message=threading.Thread(target=messaging)
thread_message.daemon=True
thread_message.start()
while True:
    data=client_socket.recv(1024).decode()
    print(data)