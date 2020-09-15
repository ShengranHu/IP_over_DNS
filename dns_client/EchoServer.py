import socket

def echo():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 8888))
    sock.listen(10)
    while True:
        conn, address = sock.accept()
        while True:
            data = conn.recv(2048)
            if data and data != b'exit\r\n':
                conn.send(data)
                print(data)
            else:
                conn.close()
                break


if __name__ == "__main__":
    try:
        echo()
    except KeyboardInterrupt:
        exit()