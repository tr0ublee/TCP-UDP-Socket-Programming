import socket
import sys

# UDP_PORT = sys.argv[1]
# TCP_PORT = sys.argv[2]

IP = '127.0.0.1'
TCP_PORT = 5858
BUFFER_SIZE = 1000

def __main__():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((IP , TCP_PORT))
    s.listen(1)
    conn , addr = s.accept()
    print(conn)
    print(addr)
    total = 0
    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            break
        # print("Received " + str(data))
        total += len(data)
    conn.close
    print(total)

__main__()