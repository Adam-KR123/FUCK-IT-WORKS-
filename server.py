
import socket
import threading
from datetime import datetime
import mysql.connector

host_name         = socket.gethostname()
host              = socket.gethostbyname(host_name)
port              = 8000
connected_clients = list()
all_clients 	  = 0

database=mysql.connector.connect(
	host="127.0.0.1",
	user="root",
	password="",
	database="text_database"
)
#0 index= table's name
db_tables=[["users","username","account_password","mac_adress"]]

class Client:
	username_conf=False
	def __init__(self, name, sck):
		self.name   = name
		self.socket = sck
	def to_string(self):
		return f"{self.name};{self.socket}"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))

def client_len():
	return len(connected_clients)

def client_by_name(name):
	for client in connected_clients:
		if client.name == name:
			return client

def nowtime_format():
	now = datetime.now()
	return now.strftime("%Y-%m-%d %H:%M:%S")

def recv():
	cl = connected_clients[client_len()-1]
	name_index=0
	client_mac_adress = cl.socket.recv(1024).decode()
	while True:
		try:
			data = cl.socket.recv(1024).decode()
			name_isFree=True
			if(name_index==0):
				try:
					mycursor=database.cursor()
					mycursor.execute(f"SELECT * FROM {db_tables[0][0]}")
					database_users=mycursor.fetchall()
					for user in database_users:
						if(user[0]==data):
							client_message(cl, f"{data} is in use. Please select another username!")
							name_isFree = False
							break
				except Exception as e:
					print(e)
				if(name_isFree):
					client_message(cl,"True")
					cl.name=data
					sql_sender=list()
					sql_sender.append(cl.name)
					sql_sender.append(client_mac_adress)
					mycursor.execute(f"INSERT INTO users ({db_tables[0][1]},{db_tables[0][3]}) VALUES (%s,%s)",sql_sender)
					database.commit()
					broadcast_message_except(f"{cl.name} joined. Headcount: {client_len()}", cl)
					client_message(cl, f"{spacer(60)}\nWelcome, your name is {cl.name}. Current headcount is {client_len()}.\n{spacer(60)}")
					cl.username_conf=True
					name_index+=1
				continue
			handle_message(cl, data)
		except Exception as e:
			print(e)
			print(f"Connection is closed ({cl.to_string()})")
			mycursor.execute(f"DELETE FROM {db_tables[0][0]} WHERE {db_tables[0][1]}= '{cl.name}'")
			database.commit()
			connected_clients.remove(cl)
			broadcast_message(f"{cl.name} disconnected. Headcount: {client_len()}")
			break

def handle_message(client, msg):
	if msg.startswith("!"):
		handle_cmd(client, msg.replace("!", "", 1))
	else:
		msg = f"[{nowtime_format()}] {client.name}: {msg}"
		print(msg)
		broadcast_message(msg)

def args_to_msg(args):
	message = ""
	for piece in args: message = message + " " + piece
	return message

def handle_cmd(client, cmd):
	parts = cmd.split(" ")
	cmd_name = parts[0].replace("!", "", 1)
	cmd_args = parts[1:]

	if cmd_name == "help":
		client_message(client, "[CMD] Available commands: \"help\", \"pm <user> <message>\", \"datetime\"")
	elif cmd_name == "pm":
		try_name = cmd_args[0]
		recipient = client_by_name(try_name)
		if not recipient:
			client_message(client, f"[CMD] No user with the name \"{try_name}\"")
			return
		if len(cmd_args[1:]) < 1:
			client_message(client, f"[CMD] No args, use !help for correct usage")
			return
		client_message(client, f"[{nowtime_format()}] You -> {client.name}: {args_to_msg(cmd_args[1:])}")
		client_message(recipient, f"[{nowtime_format()}] {client.name} -> You: {args_to_msg(cmd_args[1:])}")
	elif cmd_name == "datetime":
		client_message(client, "[CMD] Current datetime is: " + nowtime_format())


def exit_check():
	if input() == "exit":
		mycursor = database.cursor()
		mycursor.execute(f"DELETE FROM {db_tables[0][0]}")
		database.commit()
		sock.close()
exit_thread = threading.Thread(target=exit_check)
exit_thread.daemon = True
exit_thread.start()

def client_message(client, data):
	client.socket.send(bytes(data, encoding="utf-8"))#.encode()

def broadcast_message(data):
	for client in connected_clients:
		if(client.username_conf==True):
			client_message(client, data)

def broadcast_message_except(data, exclient):
	for client in connected_clients:
		if client == exclient: continue
		client_message(client, data)

def spacer(n):
	return "-"*n

while True:
	sock.listen()
	conn, addr = sock.accept()
	print(f"Connected by {addr} + conn:{conn}")

	all_clients = all_clients + 1
	new_client = Client("Anon" + str(all_clients), conn)
	connected_clients.append(new_client)

	msg_thread = threading.Thread(target=recv)
	msg_thread.daemon=True
	msg_thread.start()
