import socket
import threading
import curses

def receive_updates(client_socket, stdscr, document):
    """Receive updates from the server and update the screen."""
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            
            document[:] = data.split("\n")  # Update the local document
            render_document(stdscr, document)
        except Exception as e:
            break

def render_document(stdscr, document):
    """Render the document on the screen."""
    stdscr.clear()
    for idx, line in enumerate(document):
        stdscr.addstr(idx, 0, line)
    stdscr.refresh()

def start_client(host='172.28.26.254', port=12345):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    document = [""]  # Empty document initially

    def main(stdscr):
        curses.curs_set(1)  # Show the cursor
        stdscr.clear()

        # Initialize cursor position
        cursor_y, cursor_x = 0, 0

        # Start a thread to receive updates from the server
        receive_thread = threading.Thread(target=receive_updates, args=(client_socket, stdscr, document))
        receive_thread.daemon = True
        receive_thread.start()

        while True:
            try:
                key = stdscr.getch()

                if key == curses.KEY_UP:
                    cursor_y = max(0, cursor_y - 1)  # Move up
                elif key == curses.KEY_DOWN:
                    cursor_y = min(len(document) - 1, cursor_y + 1)  # Move down
                elif key == curses.KEY_LEFT:
                    cursor_x = max(0, cursor_x - 1)  # Move left
                elif key == curses.KEY_RIGHT:
                    cursor_x = min(len(document[cursor_y]), cursor_x + 1)  # Move right
                elif key == curses.KEY_BACKSPACE:
                    if cursor_x > 0:
                        document[cursor_y] = document[cursor_y][:cursor_x-1] + document[cursor_y][cursor_x:]
                        cursor_x -= 1
                else:
                    # Handle regular characters
                    char = chr(key)
                    document[cursor_y] = document[cursor_y][:cursor_x] + char + document[cursor_y][cursor_x:]
                    cursor_x += 1
                
                # Send the update to the server
                update_data = f"{cursor_y}:{char}:{cursor_x}"
                client_socket.sendall(update_data.encode())

                # Render the updated document locally
                render_document(stdscr, document)
                stdscr.move(cursor_y, cursor_x)  # Move cursor to the updated position
            except Exception as e:
                break

    curses.wrapper(main)

if __name__ == "__main__":
    start_client()
