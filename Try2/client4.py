import socket
import json
import os
# Definim informatiile despre server
HOST = 'localhost'
PORT = 8080

def send_request(sock, request):
    sock.sendall(json.dumps(request).encode())
    response = sock.recv(1024).decode().strip()
    print(response)

# Conectarea la server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))

    # Autentificare utilizator
    username = input("Introduceti numele de utilizator: ")
    files = []
    while True:
        file_path = r"" + input("Introduceti calea fisierului de publicat (sau lasati gol daca ati terminat): ")
        file_path = file_path.replace('"', '')
        if file_path == "":
            break
        if os.path.isfile(file_path):
            files.append(os.path.basename(file_path))
        else:
            print(f"Fisierul {os.path.basename(file_path)} nu exista sau nu este un fisier valid.")

    send_request(sock, {"username": username,"files":files})

    # Obtinerea listei de fisiere disponibile
    send_request(sock, {"type": "list"})

    while True:
        # Afisam optiunile disponibile
        print("Alegeti o optiune:")
        print("1. Descarcare fisier")
        print("2. Adaugare fisier")
        print("3. Stergere fisier")
        print("4. Iesire")

        option = input()

        if option == "1":
            # Descarcare fisier
            filename = input("Introduceti numele fisierului: ")
            owner = input("Introduceti numele proprietarului fisierului: ")
            send_request(sock, {"type": "download", "filename": filename, "owner": owner})

            # Primirea continutului fisierului si scrierea acestuia pe disk
            with open(filename, "wb") as f:
                while True:
                    data = sock.recv(1024)
                    if not data:
                        break
                    f.write(data)
                print(f"Fisierul {filename} a fost descarcat.")

        elif option == "2":
            # Adaugare fisier
            file_path = r"" + input("Introduceti calea fisierului de publicat: ")
            file_path = file_path.replace('"', '')
            send_request(sock, {"type": "nou", "filename": file_path})
            print(f"Fisierul {file_path} a fost adaugat.")

        elif option == "3":
            # Stergere fisier
            filename = input("Introduceti numele fisierului: ")
            send_request(sock, {"type": "stergere", "filename": filename})
            print(f"Fisierul {filename} a fost sters.")

        elif option == "4":
            # Inchidere client
            send_request(sock, {"type": "exit"})
            break

        else:
            print("Optiune invalida.")
