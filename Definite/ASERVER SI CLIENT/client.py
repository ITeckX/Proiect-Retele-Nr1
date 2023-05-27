import os
import socket
import json
import threading
HOST = 'localhost'
PORT = 8080

files_dir = []

def list_files(s):
    message = {"type":"list"}
    s.sendall(json.dumps(message).encode())
    data=s.recv(1024).decode().strip()
    if len(data) > 0:
        message = json.loads(data)
    print(message.get("list"))

def send_file(file_path,s):
  
    message = {"type": "file","file_name":os.path.basename(file_path)}
    s.sendall(json.dumps(message).encode())
    print("sent")
    
    message = s.recv(1024).decode().strip()
    success = json.loads(message).get('success')
    print(success)
    if not success:
        print("eroare")
        return
    

    with open(file_path,'rb') as file:
        files_dir.append(os.path.basename(file_path))

        while True:
            data = file.read(512)
            content = data.decode().strip()

            if not data:
                message = {"status":"over"}
            else:
                message = {"data":content,"status":"ok"}

            s.sendall(json.dumps(message).encode())

            message=s.recv(1024).decode().strip()
            success = json.loads(message).get("success")
            print(success)
            
            if success == 'over':
                print("Finish")
                return  


def recieve_file(s,folder_path,filename):
    file_name = message.get('file_name')
    save_file_path = folder_path + "/" + filename
    files_dir.append(filename)
    a = s.recv(1024).decode().strip()

    with open(save_file_path,'wb') as file:
        while True:
            mess = {'success':"ok"}
            s.sendall(json.dumps(mess).encode())

            rec = s.recv(1024).decode().strip()
            print(rec)
            mess = json.loads(rec)

            if mess.get('status') == 'ok':
                data = mess.get('data').encode()
                file.write(data)

            elif mess.get('status') == 'over':
                mess = {'success':"over"}
                s.sendall(json.dumps(mess).encode())
                return

def check_folder(s):
    folder_files = os.listdir(folder_path)
    print(f'Folder files: {folder_files}')
    print(f'Files dir: {files_dir}')
    files_to_send = []
    for file_name in folder_files:
        file_path = os.path.join(folder_path,file_name)
        

        if os.path.isfile(file_path) and file_name not in files_dir:
            files_to_send.append(file_path)
            

    if files_to_send:
        
        for file in files_to_send:
            print(f"Trimitere fisier {file} catre server")
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
        folder_path = r""+input("Introdu calea către director: ")
        folder_path = folder_path.replace('"', '')

        if os.path.isdir(folder_path):
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    send_file(file_path,s)
                    print(file_path)
            break
        else:
            print("Calea introdusă nu este un folder valid.")
    
    list_files(s)
    while True:
        check_folder(s)

        command = input("Introduceti comanda (download/list/iesire): ")

        if command == "download":
            filename = input("Introduceti numele fisierului dorit: ")

            message = {"type":"download","filename":filename}
            s.sendall(json.dumps(message).encode())
            recieve_file(s,folder_path,filename)

        elif command == "list":
            list_files(s)

        elif command == "iesire":
            message = {"type":"disconnect"}
            s.sendall(json.dumps(message).encode())
            break
    s.close()
    print("Conexiune incheiata")
    