import os
import socket
import json

HOST = 'localhost'
PORT = 8080

# se creaza socketul si se conecteaza la server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Client conectat la server")

    # se cere utilizatorului sa introduca numele de utilizator si lista de fisiere publicate
    username = input("Introduceti numele de utilizator: ")
    files = []
    while True:
        file_path = input("Introduceti calea fisierului de publicat (sau lasati gol daca ati terminat): ")
        if file_path == "":
            break
        if os.path.isfile(file_path):
            files.append(file_path)
        else:
            print(f"Fisierul {file_path} nu exista sau nu este un fisier valid.")

    # se trimite numele de utilizator si lista de fisiere publicate la server
    message = {"type": "login", "username": username, "files": files}
    s.sendall(json.dumps(message).encode())
    print(f"Utilizatorul {username} a fost autentificat cu succes.")

    # se primeste lista cu toti utilizatorii si fisierele lor publicate de catre server
    data = s.recv(1024)
    print(data)
    if len(data) > 0:
        message = json.loads(data.decode())
    else:
        print("Nu s-au primit date de la server.")


    print("Lista cu toti utilizatorii si fisierele lor publicate:")
    for user in message:
        print(f"{user}: {message[user]}")

    while True:
        command = input("Introduceti comanda (download/nou/stergere/iesire): ")
        if command == "download":
            file_name = input("Introduceti numele fisierului de descarcat: ")
            # se trimite cererea de descarcare a fisierului la server
            message = {"type": "download", "file_name": file_name}
            s.sendall(json.dumps(message).encode())

            # se primeste continutul fisierului de la server si se salveaza in sistemul de fisiere
            data = s.recv(1024)
            if data == b"404":
                print(f"Fisierul {file_name} nu exista.")
            else:
                file_path = os.path.join(os.getcwd(), file_name)
                with open(file_path, "wb") as f:
                    f.write(data)
                print(f"Fisierul {file_name} a fost descarcat cu succes.")
        elif command == "nou":
            file_path = input("Introduceti calea fisierului de publicat: ")
            if os.path.isfile(file_path):
                # se trimite cererea de publicare a noului fisier la server
                message = {"type": "nou", "file_path": file_path}
                s.sendall(json.dumps(message).encode())
                print(f"Fisierul {file_path} a fost publicat cu succes.")
            else:
                print(f"Fisierul {file_path} nu exista sau nu este un fisier valid.")
        elif command == "stergere":
            file_name = input("Introduceti numele fisierului de sters: ")
            # se trimite cererea de stergere a fisierului la server
            message = {"type": "stergere", "file_name": file_name}