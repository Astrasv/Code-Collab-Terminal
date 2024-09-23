import socket

def start_notification_server():
    # Create a UDP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("127.0.0.1", 55556))  # Bind to localhost on port 55556
    
    print("Notification server started on port 55556 (UDP)")
    
    while True:
        # Receiving notifications
        message, address = server.recvfrom(1024)
        print(f"Received notification from {address}: {message.decode('ascii')}")

start_notification_server()
