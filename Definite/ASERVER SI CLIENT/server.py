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

def send_file(file_name,conn):
 
    file_path = folder_path + "/" + file_name
    message = {"type": "file","file_name":file_name}
    conn.sendall(json.dumps(message).encode())
    print("sent")
    
    message = conn.recv(1024).decode().strip()
    success = json.loads(message).get('success')
    print(success)
    if not success:
        print("eroare")
        return
    

    with open(file_path,'rb') as file:

        while True:
            data = file.read(512)
            content = data.decode().strip()

            if not data:
                message = {"status":"over"}
            else:
                message = {"data":content,"status":"ok"}

            conn.sendall(json.dumps(message).encode())

            message=conn.recv(1024).decode().strip()#
            success = json.loads(message).get("success")
            print(success)
            
            if success == 'over':
                print("Finish")
                return  




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
            client['files'].remove(message.get('filename'))
            os.remove(folder_path + "/" + message.get('filename'))
        


        elif request == "download":
            download_name = message.get('filename')
            #message = {"accept":True}
            #conn.sendall(json.dumps(message).encode())
            send_file(download_name,conn) 
        elif request == "list":
            message = {'list':[x for x in clients if x["username"]!=username]}
            conn.sendall(json.dumps(message).encode())
        elif request == "disconnect":
            break

    client = next((client for client in clients if client["username"]==username),None)
    for file in client['files']:
        os.remove(folder_path + "/" + file)
    clients.remove(client)
    conn.close()


def authenticate_user(username):
    return True



def start_server():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == '__main__':
    start_server()