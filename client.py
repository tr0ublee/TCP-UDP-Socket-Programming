import socket
import sys

'''
SERVER_IP = sys.argv[1]
UDP_SERVER_PORT = sys.argv[2]
TCP_SERVER_PORT = sys.argv[3]
UDP_CLIENT_PORT = sys.argv[4]
TCP_CLIENT_PORT = sys.argv[5]
BUFFER_SIZE = 1000
'''

SERVER_IP = '127.0.0.1'
TCP_SERVER_PORT = 5858
TCP_CLIENT_PORT = 2755
READ_SIZE = 1000
TCP_FILENAME = "transfer_file_TCP.txt"
UDP_FILENAME = "transfer_file_UDP.txt"


def TCP():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create the socket.
    # I put the following line because whenever I restart the client code, 
    # although I close the socket, the connection was refused,
    # stating that connection is still alive. I learned that this is 
    # due to the fact that the socket is left in the TCP TIME-WAIT state.
    # The following line solves that.
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    s.bind((SERVER_IP, TCP_CLIENT_PORT)) # Set client's port and bind socket to SERVER_IP and TCP_CLIENT_PORT.
    s.connect((SERVER_IP, TCP_SERVER_PORT))  # Connect to server with ip SERVER_IP and listening the port TCP_SERVER_PORT
    with open(TCP_FILENAME, 'rb') as f: # read binary TCP file.
        while True:
            message = f.read(READ_SIZE) # read READ_SIZE (1000) bytes.
            if not message: #  Reached to eof. We are done.
                break
            s.send(message) # Send the message that is read from the disk.
    s.close() # Be nice and close the socket so that port will not stay open.

def UDP():
    return 0

def __main__():
    TCP() # Do TCP.
    UDP() # DO UDP.


__main__()