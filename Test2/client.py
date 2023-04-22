import socket
import pickle

SERVER = 'localhost'
PORT = 8080

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER, PORT))

username = input("Enter your username: ")
files = []

credentials = {"username": username, "files": files}
message_bytes = pickle.dumps(credentials)
message_length = len(message_bytes)
length_bytes = message_length.to_bytes(4, byteorder="big")
client_socket.send(length_bytes)
client_socket.send(message_bytes)

response = pickle.loads(client_socket.recv(1024))
users = response["users"]
print("Connected users: ", users)

def send_message(message):
    message_bytes = pickle.dumps(message)
    message_length = len(message_bytes)
    length_bytes = message_length.to_bytes(4, byteorder="big")
    client_socket.send(length_bytes)
    client_socket.send(message_bytes)

def receive_message():
    length_bytes = client_socket.recv(4)
    message_length = int.from_bytes(length_bytes, byteorder="big")
    message_bytes = client_socket.recv(message_length)
    message = pickle.loads(message_bytes)
    return message

def download_file():
    # primim numele de utilizator de la care dorim sa descarcam fisierul
    username = input("Enter the username of the user who owns the file: ")
    # primim numele fisierului pe care dorim sa-l descarcam
    filename = input("Enter the name of the file you want to download: ")
    # trimitem numele de utilizator si numele fisierului la server pentru a solicita descarcarea
    send_message({"username": username, "filename": filename})
    # primim raspunsul de la server
    response = receive_message()
    # verificam daca s-a produs o eroare
    if response["status"] == "error":
        print(response["message"])
    else:
    # deschidem fisierul si scriem continutul primit de la server
        with open(filename, "wb") as file:
            file.write(response["content"])
        print("File downloaded successfully")

def show_menu():
    print("1. Download a file")
    print("2. Exit")
    while True:
        show_menu()
        choice = input("Enter your choice: ")
        if choice == "1":
            download_file()
        elif choice == "2":
            break
        else:
            print("Invalid choice")



def main():
    show_menu()
    client_socket.close()

if __name__ == "__main__":
    main()