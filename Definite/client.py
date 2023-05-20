import os
import socket
import json
import threading
HOST = 'localhost'
PORT = 8080

files_dir = []

def send_file(file_path,s):
    with open(file_path,'rb') as file:
        file_name = os.path.basename(file_path)
        s.sendall(file_name.encode())
        files_dir.append(file_name)
        while True:
            data = file.read(1024)
            if not data:
                break
            s.sendall(data)
        print(f'Fisierul {file_name} transmis cu succes')

def check_folder(s):
    folder_files = os.listdir(folder_path)

    for file_name in folder_files:
        file_path = os.path.join(folder_path,file_name)
        files_to_send = []

        if os.path.isfile(file_path) and file_name not in files_dir:
            print(f"Trimitere fisier {file_name} catre server")
            files_to_send.append(file_path)
            

    if files_to_send:
        message = {"type":"fileNumber","number":len(files_to_send)}

        for file in files_to_send:
            send_file(file,s)

        files_to_send.clear()

    for file_name in files_dir:
        if file_name not in folder_files:
            print(f"Fisierul {file_name} a fost sters, comunicare server")
            message = {"type": "delete", "filename":file_name}
            s.sendall(json.dumps(message).encode())


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST,PORT))
    print("Conexiune stabilita cu succes")

    username = input("Nume utilizator: ")
    message = {"type":"username","username":username}
    s.sendall(json.dumps(message).encode())

    while True:
        folder_path = r"" +  input("Introdu calea către director: ")
        folder_path = folder_path.replace('"', '')

        if os.path.isdir(folder_path):
            message = {"type":"fileNumber","number":len(os.listdir(folder_path))}
            s.sendall(json.dumps(message).encode())
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    send_file(file_path,s)
                    print(file_path)
            break
        else:
            print("Calea introdusă nu este un folder valid.")
    
    data = s.recv(1024).decode().strip()
    if len(data)>0:
        files_list = json.loads(data)
    else:
        print("Nu exista fisiere postate")

    while True:
        check_folder(s)

        command = input("Introduceti comanda (download/nou/stergere/list/iesire): ")

        if command == "download":
            filename = input("Introduceti numele fisierului dorit: ")
            message = {"type":"download","file":filename}
            s.sendall(json.dumps(message).encode())

            data=s.recv(1024).decode().strip()
            if len(data) > 0:
                message = json.loads(data)

            if message.get("accept",False):
                downloaded_file = folder_path + '/' + filename
                with open(downloaded_file,'wb') as file:
                    while True:
                        data = s.recv(1024)
                        if not data:
                            break
                        file.write(data)
                print("Fisier descarcat")
            else:
                print("Cerere respinsa de catre detinatorul fisierului")

        # elif command == "nou":
        #     pass
        # elif command == "stergere":
        #     pass
        elif command == "list":
            message = {"type":"list"}
            s.sendall(json.dumps(message).encode())
            data=s.recv(1024).decode().strip()
            if len(data) > 0:
                message = json.loads(data)
            print(message.get("list"))

        elif command == "iesire":
            message = {"type":"disconnect"}
            s.sendall(json.dumps(message).encode())
            break

    print("Conexiune incheiata")
    
    
