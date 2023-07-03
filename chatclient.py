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

    try:
        marshaled_reply = server_sock.recv(1024)
        reply = pickle.loads(marshaled_reply)
        if reply != "ACK":
            print("Error: Invalid username or password")
            exit(1)
        else:
            print("Login successful.")
            # Prompt for message after successful login
            send_message(server_sock)
    except EOFError:
        print("Error: Failed to receive response from the server.")
        exit(1)

    server_sock.close()

def send_message(server_sock):
    dest = input("ENTER DESTINATION: ")
    msg = input("ENTER MESSAGE: ")

    src = me  # Set the source to `me` variable

    msg_pack = {
        'message': msg,
        'destination': dest,
        'source': src
    }

    marshaled_msg_pack = pickle.dumps(msg_pack)
    print("Sending marshaled_msg_pack:", marshaled_msg_pack)
    server_sock.send(marshaled_msg_pack)

    try:
        marshaled_reply = server_sock.recv(1024)
        reply = pickle.loads(marshaled_reply)
        if reply != "ACK":
            print("Error: Server did not accept the message (dest does not exist?)")
        else:
            print("Message sent successfully.")
    except EOFError:
        print("Error: Failed to receive response from the server.")

def main():
    try:
        me = str(sys.argv[1])
    except:
        print('Usage: python3 chatclient.py <Username>')
        exit(1)

    # Prompt for login credentials
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    login(username, password)

if __name__ == '__main__':
    main()
