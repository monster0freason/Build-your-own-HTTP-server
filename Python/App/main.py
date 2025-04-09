import socket  # noqa: F401


def main():
    server_socket = socket.create_server(("localhost", 4221))
    server_socket.settimeout(1)
    
    try:
        conn = None
        while True:
            conn = None
            
            try:
                    
                try:    
                    # Wait for a connection
                    conn, addr = server_socket.accept()
                    print(f"connection from {addr}")
                except socket.timeout:
                    continue    

                # Receive data from the client
                data = conn.recv(1024).decode('utf-8')
                print(f"received {data}")

                request_lines = data.split("\r\n")
                if not request_lines:
                    print("request is empty")
                    conn.close()
                    continue

                request_line = request_lines[0]

                try:
                    method , path , http_version = request_line.split(" ")
                except ValueError as e:
                    print(f"could not parse request line: {request_line}")

                    response ="HTTP/1.1 400 Bad Request\r\n\r\n"

                    conn.sendall(response.encode())
                    conn.close    
                    continue

                print(f"method: {method} path: {path} http_version: {http_version}")

                # --- Routing and response construction ---

                if method == "GET":
                    if path == "/":
                        response_body = "<h1>Welcome to home page</h1>"
                        response = (
                            "HTTP/1.1 200 OK\r\n"
                            "content-type: text/html\r\n"
                            f"content-length: {len(response_body.encode('utf-8'))} \r\n"
                            "\r\n"
                            f"{response_body}"
                        )

                        print("sending 200 OK for /")
                        conn.sendall(response.encode('utf-8'))

                    elif path == "/index.html":
                        try:
                            with open("app/index.html", "r" , encoding="utf-8") as f:
                                response_body = f.read()
                            content_length = len(response_body.encode('utf-8'))

                            response =(
                                "HTTP/1.1 200 OK\r\n"
                                "content-type: text/html\r\n"
                                f"content-length: {content_length}\r\n"
                                "\r\n"
                                f"{response_body}"
                            )    

                            print("sending 200 OK for index.html")
                            conn.sendall(response.encode('utf-8'))

                        except FileNotFoundError:
                            response_body = "<h1>404 Not Found</h1><p>index.html not found.</p>"
                            response = (
                                "HTTP/1.1 404 Not Found\r\n"
                                "Content-Type: text/html\r\n"
                                f"Content-Length: {len(response_body.encode('utf-8'))}\r\n"
                                "\r\n"
                                f"{response_body}"
                            )
                            print("index.html not found, sending 404")
                            conn.sendall(response.encode("utf-8")) 
                    else:
                        # Handle other paths with 404 Not Found
                        response_body = "404 Not Found"
                        response = (
                            "HTTP/1.1 404 Not Found\r\n"
                            "Content-Type: text/plain\r\n"
                            f"Content-Length: {len(response_body)}\r\n"
                            "\r\n"
                            f"{response_body}"
                        )
                        print(f"Sending 404 Not Found for {path}")
                        conn.sendall(response.encode('utf-8'))
                else:
                    # Handle methods other than GET (Method Not Allowed)
                    response_body = "405 Method Not Allowed"
                    response = (
                        "HTTP/1.1 405 Method Not Allowed\r\n"
                        "Content-Type: text/plain\r\n"
                        f"Content-Length: {len(response_body)}\r\n"
                        "\r\n"
                        f"{response_body}"
                    )
                    print(f"Sending 405 Method Not Allowed for method {method}")
                    conn.sendall(response.encode('utf-8'))

            except Exception as e:
                print(f"An error occurred: {e}")
                
                if conn:
                    try:
                        error_response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
                        conn.sendall(error_response.encode('utf-8'))
                    except Exception as send_e:
                        print(f"Failed to send error response: {send_e}")

            finally:
                
                if conn:
                    conn.close()
                    print("Connection closed\n")
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        server_socket.close()
        print("Server socket closed.")
        print("Server stopped.")                
        

if __name__ == "__main__":
    main()
                




