import socket

def main():

    server_socket = socket.create_server(('localhost', 8080) )

    try:
        print("waiting for connection...")
        client_socket , addr = server_socket.accept()
        print(f"connected to {addr}")

        data = client_socket.recv(1024).decode()
        print(f"received data: {data}")

        response = "HTTP/1.1 200 OK\r\n\r\nHello, World!"
        client_socket.sendall(response.encode())

        print("response sent")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()
        server_socket.close()
        print("server closed")


if __name__ == "__main__":
    main()