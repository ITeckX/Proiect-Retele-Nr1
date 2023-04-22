import socket
import threading
import json
# Definirea informatiilor despre server
HOST = 'localhost'
PORT = 8080

# Definirea structurii de stocare a informatiilor clientilor conectati la server
clients = {}
clients_lock = threading.Lock()

# Functie pentru gestionarea cererilor primite de la clienti
def handle_client(conn, addr):

    data = conn.recv(1024).decode().strip()
    
    if len(data) > 0:
        message = json.loads(data)

    else:
        print("Nu s-au primit date de client.")
    username = message['username']
    files = message['files']
    # Verificare credentiale client
    # In cazul in care nu sunt valide, inchidem conexiunea
    # In caz contrar, adaugam clientul in lista de clienti conectati la server
    if not authenticate_user(username):
        conn.sendall(b"Credentiale invalide. Conexiunea se va inchide.\n")
        conn.close()
        return

    clients_lock.acquire()
    clients[username] = {'address': addr, 'files': []}
    clients_lock.release()

    # Trimitem lista cu fisierele publicate de ceilalti clienti autentificati
    conn.sendall(get_file_list(username))

    # Notificam ceilalti clienti autentificati despre noua conexiune
    notify_clients(username)

    # Procesarea cererilor clientului
    while True:
        data = conn.recv(1024).decode().strip()
        if not data:
            break

        # Descarcare fisier de la alti clienti
        if data.startswith("download"):
            filename = data.split()[1]
            owner = data.split()[2]
            download_file(conn, username, filename, owner)

        # Adaugare fisier in directorul gazda expus de catre client
        elif data.startswith("add"):
            filename = data.split()[1]
            clients_lock.acquire()
            clients[username]['files'].append(filename)
            clients_lock.release()

            # Notificare despre adaugarea noului fisier
            notify_clients(username)

        # Stergere fisier din directorul gazda expus de catre client
        elif data.startswith("delete"):
            filename = data.split()[1]
            clients_lock.acquire()
            clients[username]['files'].remove(filename)
            clients_lock.release()

            # Notificare despre stergerea fisierului
            notify_clients(username)

    # Inchidem conexiunea si notificam ceilalti clienti despre deconectarea clientului respectiv
    clients_lock.acquire()
    del clients[username]
    clients_lock.release()
    notify_clients(username)
    conn.sendall(b"Conexiunea s-a inchis.")
    conn.close()


# Functie pentru autentificarea unui utilizator
def authenticate_user(username):
    return True


# Functie pentru obtinerea listei cu fisierele publicate de ceilalti clienti autentificati
def get_file_list(username):
    file_list = []
    clients_lock.acquire()
    for client in clients:
        if client != username:
            file_list.extend(clients[client]['files'])
    clients_lock.release()
    return str(file_list).encode()


# Functie pentru notificarea clientilor despre noua conexiune sau despre adaugarea/stergerea unui fisier
def notify_clients(username):
    message = f"{username} a adaugat fisierul {clients[username]['files'][-1]}" if clients[username]['files'] else f"{username} s-a conectat."
    clients_lock.acquire()
    for client in clients:
        if client != username:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect(clients[client]['address'])
            conn.sendall(message.encode())
            conn.sendall(get_file_list())
            conn.close()
    clients_lock.release()


# Functie pentru descarcarea unui fisier de la alti clienti
def download_file(conn, username, filename, owner):
    if owner not in clients or filename not in clients[owner]['files']:
        conn.sendall(f"Fisierul {filename} nu exista sau nu poate fi descarcat.".encode())
        return

    conn.sendall(f"Descarcare fisier {filename} de la {owner} in curs de desfasurare.".encode())

    # Trimitem cererea de citire a fisierului catre proprietarul acestuia
    owner_address = clients[owner]['address']
    owner_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    owner_conn.connect(owner_address)
    owner_conn.sendall(f"read {filename}".encode())

    # Primim continutul fisierului si il trimitem catre clientul care a solicitat descarcarea
    file_content = owner_conn.recv(1024)
    while file_content:
        conn.sendall(file_content)
        file_content = owner_conn.recv(1024)

    owner_conn.close()


# Functie pentru pornirea serverului
def start_server():
    # Cream socket-ul pentru server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        # Asteptam conexiuni de la clienti
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == '__main__':
    start_server()