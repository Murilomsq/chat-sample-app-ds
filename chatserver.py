from socket import *
import pickle
import const
import threading
import hashlib


salt = "5gz"

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

# Create user objects
user1 = User("Alice", hashlib.sha256((salt + "pass123").encode()).hexdigest())
user2 = User("bob", hashlib.sha256((salt + "pass456").encode()).hexdigest())
user3 = User("charlie", hashlib.sha256((salt + "pass789").encode()).hexdigest())

# Store user objects in a list
users = [user1, user2, user3]

def handle_client(conn, addr):
    try:
        # Receive login request from client
        marshaled_login_data = conn.recv(1024)
        login_data = pickle.loads(marshaled_login_data)
        username = login_data['username']
        password = login_data['password']

        # Validate login credentials
        authenticated = False
        for user in users:
            if user.username == username and user.password == password:
                authenticated = True
                break

        if authenticated:
            conn.send(pickle.dumps("ACK"))  # send ACK to client
        else:
            conn.send(pickle.dumps("NACK"))  # send NACK to client
            return

        # Wait for the message from the client
        marshaled_msg_pack = conn.recv(1024)   # receive data from client
        msg_pack = pickle.loads(marshaled_msg_pack)
        msg = msg_pack[0]
        dest = msg_pack[1]
        src = msg_pack[2]
        print("RELAYING MSG: " + msg + " - FROM: " + src + " - TO: " + dest)

        # Check if the destination exists
        try:
            dest_addr = const.registry[dest] # get address of destination in the registry
        except KeyError:
            conn.send(pickle.dumps("NACK")) # send a proper error code
            return
        else:
            conn.send(pickle.dumps("ACK")) # send ACK to client

        # Forward the message to the recipient client
        client_sock = socket(AF_INET, SOCK_STREAM) # socket to connect to clients
        dest_ip = dest_addr[0]
        dest_port = dest_addr[1]

        try:
            client_sock.connect((dest_ip, dest_port))
        except ConnectionRefusedError:
            print("Error: Destination client is down")
            return

        msg_pack = (msg, src)
        marshaled_msg_pack = pickle.dumps(msg_pack)
        client_sock.send(marshaled_msg_pack)
        marshaled_reply = client_sock.recv(1024)
        reply = pickle.loads(marshaled_reply)

        if reply != "ACK":
            print("Error: Destination client did not receive message properly")
        else:
            pass

        client_sock.close()

    finally:
        conn.close()

def start_server():
    server_sock = socket(AF_INET, SOCK_STREAM)
    server_sock.bind(('0.0.0.0', const.CHAT_SERVER_PORT))
    server_sock.listen(5)

    print("Chat Server is ready...")

    while True:
        conn, addr = server_sock.accept()
        print("Chat Server: client is connected from address " + str(addr))

        # Start a new thread to handle the client connection
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start_server()
