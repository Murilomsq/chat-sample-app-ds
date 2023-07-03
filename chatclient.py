from socket import *
import sys
import pickle
import threading
import const
import hashlib

class RecvHandler(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.client_socket = sock

    def run(self):
        while True:
            (conn, addr) = self.client_socket.accept()
            marshaled_msg_pack = conn.recv(1024)
            msg_pack = pickle.loads(marshaled_msg_pack)
            print("\nMESSAGE FROM: " + msg_pack[1] + ": " + msg_pack[0])
            conn.send(pickle.dumps("ACK"))
            conn.close()

def send_message():
    dest = input("ENTER DESTINATION: ")
    msg = input("ENTER MESSAGE: ")

    try:
        server_sock = socket(AF_INET, SOCK_STREAM)
        server_sock.connect((const.CHAT_SERVER_HOST, const.CHAT_SERVER_PORT))
    except:
        print("Server is down. Exiting...")
        exit(1)

    src = me  # Set the source to `me` variable
    
    msg_pack = (msg, dest, src)
    marshaled_msg_pack = pickle.dumps(msg_pack)
    print("Received marshaled_msg_pack:", marshaled_msg_pack) 
    server_sock.send(marshaled_msg_pack)
    
    marshaled_reply = server_sock.recv(1024)
    reply = pickle.loads(marshaled_reply)
    if reply != "ACK":
        print("Error: Server did not accept the message (dest does not exist?)")
    else:
        pass
    server_sock.close()

def send_handler():
    while True:
        send_message()

def login(username, password):
    try:
        server_sock = socket(AF_INET, SOCK_STREAM)
        server_sock.connect((const.CHAT_SERVER_HOST, const.CHAT_SERVER_PORT))
    except:
        print("Server is down. Exiting...")
        exit(1)

    salt = "5gz"  # Salt value

    login_data = {
        'username': username,
        'password': hashlib.sha256((salt + password).encode()).hexdigest()
    }

    marshaled_login_data = pickle.dumps(login_data)
    server_sock.send(marshaled_login_data)

    marshaled_reply = server_sock.recv(1024)
    reply = pickle.loads(marshaled_reply)
    if reply != "ACK":
        print("Error: Invalid username or password")
        exit(1)

    server_sock.close()

def handle_login(conn, login_data):
    username = login_data.get('username')
    password = login_data.get('password')
    
    # Check if the username and password match
    if authenticate_user(username, password):
        # Send acknowledgment back to the client
        conn.send(pickle.dumps("ACK"))
    else:
        # Send error message back to the client
        conn.send(pickle.dumps("Error: Invalid username or password"))

def authenticate_user(username, password):
    # This is just a dummy example
    # Replace this with your own authentication logic
    # Connect to your authentication system or database and perform the necessary checks
    
    # Example: Hardcoded username and password for demonstration purposes
    if username == "admin" and password == "password":
        return True
    else:
        return False

try:
    me = str(sys.argv[1])
except:
    print('Usage: python3 chatclient.py <Username>')
    exit(1)

# Prompt for login credentials
username = input("Enter your username: ")
password = input("Enter your password: ")
login(username, password)

client_sock = socket(AF_INET, SOCK_STREAM)
my_port = const.registry[me][1]
client_sock.bind(('0.0.0.0', my_port))
client_sock.listen(0)

recv_handler = RecvHandler(client_sock)
recv_handler.start()

send_thread = threading.Thread(target=send_handler)
send_thread.start()
