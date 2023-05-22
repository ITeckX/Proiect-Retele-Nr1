import os
import socket
import json
import threading

# file_name = 'cerinta'
# print(f'Fisierul {file_name} a fost sters, comunicare server')
# print(os.listdir("D:\Proiect Retele\Proiect-Retele-Nr1\Definite\Fisiere_Client1"))
# print(len(os.listdir("D:\Proiect Retele\Proiect-Retele-Nr1\Definite\Fisiere_Client1")))
# files_dir = []

# folder_path = r"" +  input("Introdu calea către director: ")
# folder_path = folder_path.replace('"', '')

# if os.path.isdir(folder_path):
#     for root, dirs, files in os.walk(folder_path):
#         for file in files:
#             file_path = os.path.join(root, file)
#             file_name = os.path.basename(file_path)
#             print(file_name)
#             files_dir.append(file_name)
            
            
# else:
#     print("Calea introdusă nu este un folder valid.")

# import threading
# import socket

# def handle_notifications(client_socket):
#     client_address = client_socket.getpeername()  # Adresa clientului

#     if client_address == ('adresa_serverului_notificari', portul_serverului_notificari):
#         # Cod pentru tratarea notificărilor
#         while True:
#             notification = client_socket.recv(1024)  # Primește notificări de la server

#             # Implementați codul dvs. pentru tratarea notificărilor aici
#             # Poate fi un mesaj sau o acțiune specifică
#     else:
#         # Cod pentru tratarea conexiunii clientului obișnuit
#         while True:
#             data = client_socket.recv(1024)  # Primește date de la client

#             # Implementați codul dvs. pentru tratarea datelor de la client aici
#             # Poate fi un mesaj sau o acțiune specifică

# def main():
#     # Creează un socket pentru primirea conexiunilor de notificări
#     notification_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     notification_socket.bind(('adresa_locala', portul_local))
#     notification_socket.listen(1)

#     while True:
#         client_socket, client_address = notification_socket.accept()

#         # Creează un thread separat pentru tratarea fiecărei conexiuni
#         client_thread = threading.Thread(target=handle_notifications, args=(client_socket,))
#         client_thread.start()

# if __name__ == '__main__':
#     main()

# clients = []

# clients.append({"name":"calin","muie":'Muie'})
# clients.append({"name":"calin2"})
# clients.append({"name":"calin3"})

# print(clients)

message = {"success":True}
print(type(message) is dict)