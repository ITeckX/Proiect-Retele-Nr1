import os
import socket
import json
import threading
HOST = 'localhost'
PORT = 8080

files_dir = []

def send_file(file_path,socket):
    with open(file_path,'rb') as file:
        file_name = os.path.basename(file_path)
        s.sendall(file_name.encode())
        
        while True:
            data = file.read(1024)
            if not data:
                break
            s.sendall(data)
        print("Fisier transmis cu succes")




with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST,PORT))
    print("Conexiune stabilita cu succes")

    username = input("Nume utilizator: ")
    message = {"type":"username","username":username}
    s.sendall(json.dumps(message).encode())
    folder_path = r"" +  input("Introdu calea către director: ")
    folder_path = folder_path.replace('"', '')

    if os.path.isdir(folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                send_file(file_path,s)
                files_dir.append()
                print(file_path)
    else:
        print("Calea introdusă nu este un folder valid.")
    
    data = s.recv(1024).decode().strip()
    if len(data)>0:
        files_list = json.loads(data)
    else:
        print("Nu exista fisiere postate")

    while True:
        command = input("Introduceti comanda (download/nou/stergere/list/iesire): ")
        if command == "download":
            filename = input("Introduceti numele fisierului dorit: ")
            message = {"type":"download","file":filename}
            s.sendall(json.dumps(message).encode())
            downloaded_file = folder_path + '/' + filename
            with open(downloaded_file,'wb') as file:
                while True:
                    data = s.recv(1024)
                    if not data:
                        break
                    file.write(data)
            print("Fisier descarcat")

        # elif command == "nou":
        #     pass
        # elif command == "stergere":
        #     pass
        elif command == "list":
            message = {"type":"list"}

        elif command == "iesire":
            message = {"type":"iesire"}
            s.sendall(json.dumps(message).encode())
            break

    print("Conexiune incheiata")
    
    
