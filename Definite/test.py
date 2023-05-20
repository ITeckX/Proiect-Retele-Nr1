import os
import socket
import json
import threading
files_dir = []

folder_path = r"" +  input("Introdu calea către director: ")
folder_path = folder_path.replace('"', '')

if os.path.isdir(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_name = os.path.basename(file_path)
            print(file_name)
            files_dir.append(file_name)
            
            
else:
    print("Calea introdusă nu este un folder valid.")