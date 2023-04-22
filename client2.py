import socket
import pickle

# Setări generale
SERVER = "localhost"
PORT = 8080
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
BUFFER_SIZE = 4096

# Autentificare utilizator
def authenticate(client_socket):
    # Primirea datelor de autentificare de la utilizator
    name = input("Enter your name: ")
    files = []
    auth_data = {"name": name, "files": files}
    client_socket.sendall(pickle.dumps(auth_data))

    # Așteptarea răspunsului de la server
    data = client_socket.recv(BUFFER_SIZE)
    response = pickle.loads(data)
    if response["status"] == "error":
        print(response["message"])
        return False
    else:
        print(response["message"])
        return True

# Publicare fișier
def publish_file(client_socket):
    file_name = input("Enter the name of the file you want to publish: ")
    request = {"type": "publish", "file": file_name}
    client_socket.sendall(pickle.dumps(request))

    # Așteptarea răspunsului de la server
    data = client_socket.recv(BUFFER_SIZE)
    response = pickle.loads(data)
    print(response["message"])

# Descărcare fișier
def download_file(client_socket):
    file_name = input("Enter the name of the file you want to download: ")
    request = {"type": "download", "file": file_name}
    client_socket.sendall(pickle.dumps(request))

    # Așteptarea răspunsului de la server
    data = client_socket.recv(BUFFER_SIZE)
    response = pickle.loads(data)
    if response["status"] == "error":
        print(response["message"])
    else:
        with open(file_name, "wb") as f:
            f.write(response["file_data"])
        print(f"{file_name} downloaded successfully.")

# Listare fișiere publicate de ceilalți utilizatori
def list_files(client_socket):
    request = {"type": "list"}
    client_socket.sendall(pickle.dumps(request))

    # Așteptarea răspunsului de la server
    data = client_socket.recv(BUFFER_SIZE)
    response = pickle.loads(data)
    if response["status"] == "ok":
        file_list = response["file_list"]
        print("Available files:")
        for file_name in file_list:
            print(file_name)

# Deconectare
def disconnect(client_socket):
    request = {"type": "disconnect"}
    client_socket.sendall(pickle.dumps(request))

    # Închiderea socket-ului clientului
    client_socket.close()

# Conectare la server
def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER, PORT))
    if not authenticate(client_socket):
        return
    while True:
        command = input("Enter a command (publish, download, list, disconnect): ")
        if command == "publish":
            publish_file(client_socket)
        elif command == "download":
            download_file(client_socket)
        elif command == "list":
            list_files(client_socket)
        elif command == "disconnect":
            disconnect(client_socket)
            break
        else:
            print("Invalid command. Please enter a valid command.")


if __name__ == "__main__":
    connect_to_server()