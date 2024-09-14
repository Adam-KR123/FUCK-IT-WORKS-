import socket
import threading

hostname= socket.gethostname()
host =socket.gethostbyname(hostname)
port = 8000
users=[]

class user:
    def __init__(self,name,socket):
        self.name=name
        self.socket=socket
    def __str__(self):
        return f"{self.name} ,{self.socket}"

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((host, port))

def recieving():
    current_index=users[len(users)-1]
    name_counter=0
    while True:
        data=current_index.socket.recv(1024).decode()
        if(name_counter==0):
             current_index.name=data
             name_counter+=1
             continue
        print(current_index.name+":"+data)
        for x in users:
             x.socket.send(str(current_index.name+":"+data).encode())
def quit():
     quit_check=input()
     if(quit_check=="quit"):
          s.close()
thread_quit=threading.Thread(target=quit)
thread_quit.daemon=True
thread_quit.start()
while True:
        s.listen()
        conn,addr=s.accept()
        print(f"Connected by {addr}")
        new_user= user("User"+str(len(users)+1),conn)
        users.append(new_user)
        thread_number=threading.Thread(target=recieving)
        thread_number.daemon=True
        thread_number.start()


            

