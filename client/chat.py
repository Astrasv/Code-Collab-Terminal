import socket
import threading
from code import start_client

host = "172.28.26.254"
port = 55555


nickname = input("Choose Nickname: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(10)
client.connect((host, port))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == "NICK":
                client.send(nickname.encode('utf-8'))
            elif message == "START_CODE":
                print("Starting the code client...")
                start_client()
                
                
            else:
                print(message)
        except:
            print("An error occurred!")
            client.close()
            break

def write():
    while True:
        input_msg = input("")

        if input_msg == "::code":
           
            client.send(f"{input_msg}".encode('utf-8'))
        else:
            message = f'CHAT:{nickname}: {input_msg}'
            client.send(message.encode('utf-8'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
