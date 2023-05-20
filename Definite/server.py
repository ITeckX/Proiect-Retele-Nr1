import socket
import threading
import json

HOST = 'localhost'
PORT = 8080
clients = {}
clients_lock = threading.Lock()


def handle_client(conn, addr):
    pass


def authenticate_user(username):
    return True

def start_server():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == '__main__':
    start_server()