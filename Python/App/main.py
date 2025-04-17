import socket
import threading

def build_response(status_code, status_message, headers=None, content_type=None, body=None):
    """
    Build a complete HTTP response string.
    """
    response = f"HTTP/1.1 {status_code} {status_message}\r\n"
    
    if headers:
        for key, value in headers.items():
            response += f"{key}: {value}\r\n"
    
    if content_type:
        response += f"Content-Type: {content_type}\r\n"
    
    body = body if body is not None else ""
    response += f"Content-Length: {len(body.encode('utf-8'))}\r\n"
    response += "\r\n"
    response += body
    
    return response

def route_request(method, path, headers):
    if method == "GET":
        if path == "/":
            response_body = "<h1>Welcome to home page</h1>"
            return build_response(
                200, "OK",
                content_type="text/html",
                body=response_body
            )

        elif path == "/index.html":
            try:
                with open("app/index.html", "r", encoding="utf-8") as f:
                    response_body = f.read()
                return build_response(
                    200, "OK",
                    content_type="text/html",
                    body=response_body
                )
            except FileNotFoundError:
                response_body = "<h1>404 Not Found</h1><p>index.html not found.</p>"
                return build_response(
                    404, "Not Found",
                    content_type="text/html",
                    body=response_body
                )

        elif path.startswith("/echo/"):
            msg = path[len("/echo/"):]
            return build_response(
                200, "OK",
                content_type="text/plain",
                body=msg
            )
        
        elif path.startswith("/files/"):
            directory = "App/files"
            filename = path[len("/files/"):]
            try:
                with open(f"{directory}/{filename}", "r", encoding="utf-8") as f:
                    response_body = f.read()
                return build_response(
                    200, "OK",
                    content_type="application/octet-stream",
                    body=response_body
                )
            except FileNotFoundError:
                response_body = "<h1>404 Not Found</h1><p>File not found.</p>"
                return build_response(
                    404, "Not Found",
                    content_type="text/html",
                    body=response_body
                )


        elif path == "/user-agent":
            user_agent = headers.get("User-Agent", ["Unknown"])[0]
            return build_response(
                200, "OK",
                content_type="text/plain",
                body=user_agent
            )

        else:
            return build_response(
                404, "Not Found",
                content_type="text/plain",
                body="404 Not Found"
            )
    else:
        return build_response(
            405, "Method Not Allowed",
            content_type="text/plain",
            body="405 Method Not Allowed"
        )

def handle_connection(conn):
    try:
        data = conn.recv(1024).decode('utf-8')
        print(f"Received: {data}")

        request_lines = data.split("\r\n")
        if not request_lines:
            print("Empty request")
            return

        request_line = request_lines[0]
        headers = {h.split(": ")[0]: h.split(": ")[1:] for h in request_lines[1:] if ": " in h}

        try:
            method, path, http_version = request_line.split(" ")
        except ValueError:
            print(f"Could not parse request line: {request_line}")
            response = build_response(400, "Bad Request")
            conn.sendall(response.encode())
            return

        print(f"Method: {method}, Path: {path}, Version: {http_version}")
        response = route_request(method, path, headers)
        conn.sendall(response.encode("utf-8"))

    except Exception as e:
        print(f"An error occurred: {e}")
        try:
            error_response = build_response(500, "Internal Server Error")
            conn.sendall(error_response.encode('utf-8'))
        except Exception as send_e:
            print(f"Failed to send error response: {send_e}")

    finally:
        conn.close()
        print("Connection closed\n")

def main():
    server_socket = socket.create_server(("localhost", 4221))
    server_socket.settimeout(1)

    try:
        while True:
            try:
                conn, addr = server_socket.accept()
                print(f"Connection from {addr}")
                thread = threading.Thread(target=handle_connection, args=(conn,))
                thread.daemon = True  # Optional: allow clean exit
                thread.start()
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        server_socket.close()
        print("Server socket closed.")
        print("Server stopped.")

if __name__ == "__main__":
    main()




