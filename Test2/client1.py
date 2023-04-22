import socket
import pickle
import threading
HOST = 'localhost'
PORT = 8080

def send_message(sock, message):
    message_bytes = pickle.dumps(message)
    message_length = len(message_bytes).to_bytes(4, byteorder='big')
    sock.sendall(message_length + message_bytes)

def receive_message(sock):
    message_length_bytes = sock.recv(4)
    message_length = int.from_bytes(message_length_bytes, byteorder='big')
    message_bytes = b''
    while len(message_bytes) < message_length:
        message_chunk = sock.recv(message_length - len(message_bytes))
        if not message_chunk:
            raise EOFError("Ran out of input")
        message_bytes += message_chunk
    message = pickle.loads(message_bytes)
    return message

def authenticate_user(sock):
    username = input("Enter username: ")
    password = input("Enter password: ")
    files = input("Enter a comma-separated list of files to publish: ").split(',')
    message = {
        'command': 'authenticate',
        'username': username,
        'password': password,
        'files': files
    }
    
    send_message(sock, message)
    response = receive_message(sock)
    print(response['message'])
    return response['success']

def get_file_list(sock):
    message = {
        'command': 'get_file_list'
    }
    send_message(sock, message)
    response = receive_message(sock)
    print(response['message'])
    if response['success']:
        print("File list:")
        for file in response['files']:
            print(file)

def download_file(sock):
    filename = input("Enter filename to download: ")
    message = {
        'command': 'download_file',
        'filename': filename
    }
    send_message(sock, message)
    response = receive_message(sock)
    if response['success']:
        with open(filename, 'wb') as f:
            f.write(response['file_contents'])
        print(f"File '{filename}' downloaded successfully.")
    else:
        print(response['message'])

def handle_file_changes(sock):
    print("Monitoring file changes...")
    while True:
        event_type, event_file = input("Enter event type (add/remove) and filename: ").split()
        message = {
            'command': 'file_change',
            'event_type': event_type,
            'event_file': event_file
        }
        send_message(sock, message)
        response = receive_message(sock)
        print(response['message'])

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        authenticated = authenticate_user(sock)
        if not authenticated:
            return

        get_file_list(sock)
        download_file(sock)

        file_changes_thread = threading.Thread(target=handle_file_changes, args=(sock,))
        file_changes_thread.start()

        while True:
            command = input("Enter command (logout to exit): ")
            if command == 'logout':
                break
            elif command == 'get_file_list':
                get_file_list(sock)
            elif command == 'download_file':
                download_file(sock)

        file_changes_thread.join()

if __name__ == '__main__':
    main()
