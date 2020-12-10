import socket
import sys

# UDP_PORT = sys.argv[1] # read server listening UDP Port.
# TCP_PORT = sys.argv[2] # read server listenin TCP Port.

IP = '127.0.0.1' # Local address to bind.
TCP_PORT = 5858 
CHUNK_SIZE = 1000 # Chunk size that is sent by the client. Client sends 1000 bytes, server reads 1000 bytes.
MEGA = 1e6 # For debug purposes when checking if I received all the bytes.
TCP_FILENAME = "transfer_file_TCP.txt" # file to be read by TCP.
UDP_FILENAME = "transfer_file_UDP.txt" # file to be read by UDP.
def __main__():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create the socket.
    s.bind((IP , TCP_PORT)) # bind to IP and port.
    s.listen(1) # start listening
    conn , addr = s.accept() # accept connection requests
    total = 0 # a debug variable that shows how many byte is read.
    f = open(TCP_FILENAME, "wb")
    while True:
        data = conn.recv(CHUNK_SIZE) # receive data.
        if not data:
            break # client is done. 
        f.write(data)
        total += len(data) # DEBUG. Just to see if I am reading the file correctly.
        conn.send(bytes(True)) # send True to client to tell that 'OK, I received your message' 
    conn.close # be nice and close the connection.
    s.close() # be nice and close the socket.
    f.close()
    # print(str(total/MEGA) + " MegaBytes received") # debug

__main__()