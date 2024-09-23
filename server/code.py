import socket
import threading

# Store the shared document as a list of lines
document = [""]

# List of connected clients
clients = []

# Lock for synchronizing access to the document
document_lock = threading.Lock()

# Notification socket for sending notifications
notification_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
notification_server_address = ("127.0.0.1", 55556)

def handle_client(client_socket, addr):
    global document
    try:
        print(f"[INFO] Client {addr} connected.")
        notification_socket.sendto(f"Received notification from {addr}: User connected to Code.".encode('ascii'), notification_server_address)
        # Send the initial document to the new client
        client_socket.sendall("\n".join(document).encode())

        while True:
            # Receive changes from the client
            data = client_socket.recv(1024).decode()
            if not data:
                break

            # Handle document updates in a thread-safe manner
            with document_lock:
                # Parse incoming data, expected format: "{line_num}:{char}:{cursor_pos}"
                parts = data.split(":", 2)
                if len(parts) == 3:
                    line_num, char, cursor_pos = int(parts[0]), parts[1], int(parts[2])

                    # Update the document at the appropriate position
                    document[line_num] = document[line_num][:cursor_pos] + char + document[line_num][cursor_pos:]

            # Broadcast the updated document to all clients
            broadcast("\n".join(document), client_socket)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        print(f"[INFO] Client {addr} disconnected.")
        client_socket.close()
        clients.remove(client_socket)

def broadcast(data, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.sendall(data.encode())
            except Exception as e:
                print(f"[ERROR] Could not send to client: {e}")

def start_server(host='127.0.0.1', port=12345):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[INFO] Server started on {host}:{port}")
    
    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()


start_server()
