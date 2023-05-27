import socket
import threading
import pickle
import os
import json
# Setari generale
PORT = 8080
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
BUFFER_SIZE = 4096
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def create_server():
    # Crează un socket de tip TCP/IP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Permite folosirea aceluiași port după închiderea serverului
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Leagă socket-ul la o adresă și un port
    server_address = (SERVER, PORT)
    server_socket.bind(server_address)

    # Ascultă conexiuni de la clienți
    server_socket.listen(1)

    # Returnează obiectul socket pentru server
    return server_socket


class Client:
    def __init__(self, name, files, client_socket):
        self.name = name
        self.files = files
        self.client_socket = client_socket
class Server:
    def__init__(self):
        self.clients = []

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(ADDR)

    def start(self):
        print("Aștept conexiuni...")
        self.server_socket.listen(5)
        print(f"[SERVER] Listening on {SERVER}")

        while True:
            client_socket, client_addr = self.server_socket.accept()
            print(f"[NEW CONNECTION] {client_addr} connected.")

            # Creare thread separatpentru fiecare conexiune client-server
            thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            thread.start()
            print(f"Thread started")

    def handle_client(self, client_socket):
        # Autentificare client
        authenticated = False
        client_name = ""
        while not authenticated:
            try:
                # Primirea datelor de autentificare de la client
                data = client_socket.recv(BUFFER_SIZE)print(data)
                if data:
                    auth_data = pickle.loads(data)
                    client_name = auth_data["name"]
                    client_files = auth_data["files"]

                    # Verificare dacă numele de utilizator există deja
                    for client in self.clients:
                        if client.name == client_name:
                            response = {"status": "error", "message": "Username already taken."}client_socket.sendall(pickle.dumps(response))
                            break
                    else:
                        # Adăugare client la listă și trimiterea listei de clienți conectați
                        new_client = Client(client_name, client_files, client_socket)
                        self.clients.append(new_client)
                        response = {"status": "ok", "message": "Authentication successful."}
                        client_socket.sendall(pickle.dumps(response))
                        authenticated = True

                        # Notificare pentru ceilalți clienți despre adăugarea unui nou client
                        for client in self.clients:
                            if client.client_socket != client_socket:
                                notification = {"type": "add", "name": client_name, "files": client_files}
                                client.client_socket.sendall(pickle.dumps(notification))
            except:pass

        # Loop pentru gestionarea cererilor de la client
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if data:
                    request = pickle.loads(data)

                    # Verificare tip cerere
                    if request["type"] == "publish":
                        # Publicare fișier
                        for client in self.clients:
                            if client.client_socket == client_socket:client.files.append(request["file"])
                                response = {"status": "ok", "message": "File published."}
                                client_socket.sendall(pickle.dumps(response))
                                break

                        # Notificare pentru ceilalți clienți despre adăugarea unui fișier
                        for client in self.clients:
                            if client.client_socket != client_socket:notification = {"type": "file_add", "name": client_name, "file": request["file"]}
                                client.client_socket.sendall(pickle.dumps(notification))

                    elif request["type"] == "download":
                        # Descărcare fișier
                        file_path = os.path.join(BASE_DIR, client_name, request["file"])
                        if os.path.exists(file_path):
                            with open(file_path, "rb") as f:file_data = f.read()
                            response = {"status": "ok", "file_data": file_data}
                        else:
                            response = {"status": "error", "message": "File not found."}
                        client_socket.sendall(pickle.dumps(response))

                    elif request["type"] == "list":
                        # Trimitere listă de fișiere publicate de ceilalți clienți
                        file_list = []for client in self.clients:
                            if client.client_socket != client_socket:
                                file_list += client.files
                        response = {"status": "ok", "file_list": file_list}
                        client_socket.sendall(pickle.dumps(response))

                    elif request["type"] == "disconnect":
                        # Deconectare client și notificare pentru ceilalți clienți
                        self.clients = [client for client in self.clients if client.client_socket != client_socket]
                        response = {"status": "ok", "message": "Disconnected."}
                        client_socket.sendall(pickle.dumps(response))
                        for client in self.clients:
                            if client.client_socket != client_socket:
                                notification = {"type": "remove", "name": client_name}
                                client.client_socket.sendall(pickle.dumps(notification))
                        break
            except:
                break

        # Închidere conexiune
        print(f"[DISCONNECT] {client_name} disconnected.")
        client_socket.close()

def main():
    # Creează serverul
    server = Server()
    server.start()

if __name__ == '__main__':
    main()