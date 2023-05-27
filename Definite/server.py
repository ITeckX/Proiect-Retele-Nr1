import socket
import threading
import json
import os
HOST = 'localhost'
PORT = 8080
clients = []
folder_path = "D:\Proiect Retele\Proiect-Retele-Nr1\Definite\Fisiere_Server"


def recieve_file(conn,message,username):
    file_name = message.get('file_name')
    client = next((client for client in clients if client["username"]==username),None)
    client["files"].append(file_name)
    save_file_path = folder_path + "/" + file_name
    

    with open(save_file_path,'wb') as file:
        while True:
            mess = {'success':"ok"}
            conn.sendall(json.dumps(mess).encode())

            rec = conn.recv(1024).decode().strip()
            print(rec)
            mess = json.loads(rec)

            if mess.get('status') == 'ok':
                data = mess.get('data').encode()
                file.write(data)

            elif mess.get('status') == 'over':
                mess = {'success':"over"}
                conn.sendall(json.dumps(mess).encode())
                return
    # conn.sendall(json.dumps({"success":True}).encode())
          
    #         file_name=conn.recv(1024).decode().strip()
    #         print(file_name)
    #         client = next((client for client in clients if client["username"]==username),None)
    #         client["files"].append(file_name)

    #         save_file_path = folder_path + "/" + file_name

    #         with open(save_file_path,'wb') as file:
    #             while True:
    #                 over_rec = conn.recv(1024).decode().strip()
    #                 print(over_rec)
    #                 over = json.loads(over_rec).get("success")
    #                 print(f"Over: {str(over)}")
    #                 conn.sendall(json.dumps({"success":False}).encode())
    #                 if over:
    #                     print("finished")
    #                     break
    #                 data = conn.recv(1024)
    #                 print(data.decode().strip()+'/')
                 
    #             file.write(data)
    #             message = {"success":True}
    #             conn.sendall(json.dumps(message).encode())
    




def handle_client(conn, addr):
    
    data = conn.recv(1024).decode().strip()#
    
    if len(data) > 0:
        message = json.loads(data)

    username = message.get("username")
    clients.append({"username":username, "files":[]})

    while True:
        data = conn.recv(1024).decode().strip()
        print(data)
        if len(data) >0:
            message = json.loads(data)
    
        request = message.get("type")
        
        if not data:
            break

        if request == "file":
            recieve_file(conn,message,username)
                
        elif request == "delete":
            client = next((client for client in clients if client["username"]==username),None)
            client['files'].remove(file_name)

        elif request == "download":
            download_name = message.get('file')
            message = {"accept":True}
            conn.sendall(json.dumps(message).encode())
            send_file(conn,download_name) 
        elif request == "list":
            message = {'list':[x for x in clients if x["username"]!=username]}
            conn.sendall(json.dumps(message).encode())
        elif request == "disconnect":
            break

    conn.close()


def authenticate_user(username):
    return True

def send_file(conn,file_name):
    file_path = folder_path + "/" + file_name
    with open(file_path,'rb') as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            conn.sendall(data)
        print(f'Fisierul {file_name} transmis cu succes')

def start_server():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == '__main__':
    start_server()