import socket
import threading
import os
import pickle
import time

# definim portul și adresa IP a server-ului
PORT = 8080
SERVER = 'localhost'

# cream socket-ul
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER, PORT))

# definim un dictionar in care stocam numele de utilizator și lista de fisiere
users = {}

# definim un dictionar in care stocam socket-urile pentru fiecare client
client_sockets = {}

# definim o functie pentru trimiterea de mesaje
def send_message(client_socket, message):
    message_bytes = pickle.dumps(message)
    message_length = len(message_bytes)
    length_bytes = message_length.to_bytes(4, byteorder="big")
    client_socket.send(length_bytes)
    client_socket.send(message_bytes)

# definim o functie pentru primirea de mesaje
def receive_message(client_socket):
    length_bytes = client_socket.recv(4)
    
    message_length = int.from_bytes(length_bytes, byteorder="big")

    message_bytes = client_socket.recv(message_length)
    print(message_bytes)
    message = pickle.loads(message_bytes)
  
    return message

# definim o functie care se ocupa de autentificarea utilizatorilor
def handle_authentication(client_socket):
    while True:
        # primim numele de utilizator și lista de fisiere
        credentials = receive_message(client_socket)
        username = credentials["username"]
        files = credentials["files"]

        # verificam daca numele de utilizator este deja luat
        if username in users:
            send_message(client_socket, {"status": "error", "message": "Username already taken"})
        else:
            # adaugam utilizatorul in dictionarul users si socket-ul in dictionarul client_sockets
            users[username] = files
            client_sockets[username] = client_socket
            # trimitem lista de utilizatori si fisiere la toți utilizatorii conectați
            for user in users:
                send_message(client_sockets[user], {"type": "user_list", "users": users})
            # notificam utilizatorii ca un nou utilizator s-a conectat
            for user in users:
                if user != username:
                    send_message(client_sockets[user], {"type": "new_user", "username": username, "files": files})
            # iesim din bucla
            break

# definim o functie care se ocupa de primirea si trimiterea de fisiere
def handle_file_transfer(client_socket):
    # primim numele de utilizator si numele fisierului pe care clientul doreste sa-l descarce
    message = receive_message(client_socket)
    username = message["username"]
    filename = message["filename"]

    # verificam daca utilizatorul care detine fisierul este conectat
    if username not in users:
        send_message(client_socket, {"status": "error", "message": "User is not connected"})
        return
    # verificam daca fisierul exista in lista de fisiere ale utilizatorului
    if filename not in users[username]:
        send_message(client_socket, {"status": "error", "message": "File does not exist"})
        return

    # deschidem fisierul si citim continutul
    with open(os.path.join(username, filename), "rb") as file:
            file_content = file.read()

    # trimitem continutul fisierului catre clientul care a cerut descarcarea
    send_message(client_socket, {"status": "success", "content": file_content})

# definim o functie care se ocupa de notificarea clientilor atunci cand se adauga sau se sterge un fisier
def handle_file_changes(client_socket):
    username = None
    while True:
        # primim numele de utilizator
        if username is None:
            message = receive_message(client_socket)
            username = message["username"]
        # verificam daca directorul utilizatorului exista, altfel il cream
        if not os.path.isdir(username):
            os.mkdir(username)
        # monitorizam directorul utilizatorului pentru a detecta adaugarea sau stergerea de fisiere
        for file in os.listdir(username):
            if file not in users[username]:
                # adaugam fisierul la lista de fisiere ale utilizatorului
                users[username].append(file)
                # notificam ceilalti clienti
                for user in users:
                    if user != username:
                        send_message(client_sockets[user], {"type": "file_added", "username": username, "filename": file})
            # asteptam cateva secunde pentru a nu detecta aceeasi modificare de mai multe ori
            time.sleep(2)
        for file in users[username]:
            if file not in os.listdir(username):
                # stergem fisierul din lista de fisiere ale utilizatorului
                users[username].remove(file)
                # notificam ceilalti clienti
                for user in users:
                    if user != username:
                        send_message(client_sockets[user], {"type": "file_deleted", "username": username, "filename": file})
            # asteptam cateva secunde pentru a nu detecta aceeasi modificare de mai multe ori
            time.sleep(2)

# definim functia principala care ruleaza server-ul
def main():
    # ascultam conexiuni
    server_socket.listen()
    print(f"Server is listening on {SERVER}:{PORT}")
    while True:
        # acceptam o noua conexiune
        client_socket, address = server_socket.accept()
        print(f"New connection from {address}")
        # cream un fir de executie pentru a gestiona conexiunea
        authentication_thread = threading.Thread(target=handle_authentication, args=(client_socket,))
        authentication_thread.start()
        file_transfer_thread = threading.Thread(target=handle_file_transfer, args=(client_socket,))
        file_transfer_thread.start()
        file_changes_thread = threading.Thread(target=handle_file_changes, args=(client_socket,))
        file_changes_thread.start()

if __name__ == "__main__":
    main()

