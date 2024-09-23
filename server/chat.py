import threading
import socket

# Notification socket for sending notifications
notification_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
notification_server_address = ("127.0.0.1", 55556)

host = "127.0.0.1"
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode('ascii'))
        except Exception as e:
            print(f"Error broadcasting message to {client}: {e}")

def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            
            # Handle different message types
            if message.startswith("CHAT:"):
                broadcast(message[5:])
                nickname = message.split(":")[1].split()[0]
                send_sent_notification(nickname)
            elif message.startswith("TYPING:"):
                nickname = message.split(":")[1]
                send_typing_notification(nickname)
        
        except Exception as e:
            print(f"Error handling client {client}: {e}")
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat!')
            send_leave_notification(nickname)
            nicknames.remove(nickname)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
    
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)
        
        print(f"Nickname of client is {nickname}")
        broadcast(f'{nickname} joined the chat!')
        send_join_notification(nickname)
        client.send("Connected to the server!".encode('ascii'))
        
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

# Functions to send notifications via UDP
def send_join_notification(nickname):
    message = f"USER JOINED: {nickname}"
    notification_socket.sendto(message.encode('ascii'), notification_server_address)

def send_leave_notification(nickname):
    message = f"USER LEFT: {nickname}"
    notification_socket.sendto(message.encode('ascii'), notification_server_address)

def send_sent_notification(nickname):
    message = f"{nickname} sent a message."
    notification_socket.sendto(message.encode('ascii'), notification_server_address)

def send_typing_notification(nickname):
    message = f"{nickname} is typing..."
    notification_socket.sendto(message.encode('ascii'), notification_server_address)

print(f"Chat Server is listening on port {port}")
receive()
