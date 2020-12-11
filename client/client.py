'''
    Alperen Caykus
    2237170
'''
import socket
import sys
import time
import struct
from datetime import datetime


'''
# read server ip
SERVER_IP = sys.argv[1]
# read UDP server listening port 
UDP_SERVER_PORT = sys.argv[2]
# read TCP server listening port 
TCP_SERVER_PORT = sys.argv[3]
# read UDP client sending port 
UDP_CLIENT_PORT = sys.argv[4] 
# read TCP client sending port
TCP_CLIENT_PORT = sys.argv[5]
'''

SERVER_IP = '127.0.0.1'
TCP_SERVER_PORT = 5856
TCP_CLIENT_PORT = 2754 
# Get the size of timestamps in bytes
TIME_SIZE_IN_BYTES = sys.getsizeof(struct.pack("d",time.time()))
# Chunk size in bytes. 
CHUNK_SIZE = 1000 
# file to be sent by TCP.
TCP_FILENAME = "transfer_file_TCP.txt"
# file to be sent by UDP.
UDP_FILENAME = "transfer_file_UDP.txt" 
# multiplier to convert s to ms
MILISEC = 1e3 

'''
    A function that returns timestamp in binary.
'''
def getBinaryTimeStamp():
    start = time.time()
    return struct.pack("d", start)

def TCP():
    # create the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create the socket.
    # I put the following line because whenever I restart the client code, 
    # although I close the socket, the connection was refused,
    # stating that Address already in use. I learned that this is 
    # due to the fact that the socket is left in the TCP TIME-WAIT state.
    # The following line solves that.
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    # Set client's port and bind socket to SERVER_IP and TCP_CLIENT_PORT.
    s.bind((SERVER_IP, TCP_CLIENT_PORT)) 
    # Connect to server with ip SERVER_IP and listening the port TCP_SERVER_PORT
    s.connect((SERVER_IP, TCP_SERVER_PORT))  
    # read binary TCP file.
    with open(TCP_FILENAME, 'rb') as f: 
        while True:
            # read READ_SIZE (1000 - (TIME_STAMP_SIZE)) bytes. 
            # We will add the date time information at the beginning of the message.
            message = f.read(CHUNK_SIZE - TIME_SIZE_IN_BYTES) 
            if not message: 
                #  Reached to eof. We are done.
                break
            # get current time, convert it to string, then conver the string to bytes
            start = getBinaryTimeStamp() 
            # Send the timestamp (start) + message that is read from the disk.
            s.sendall(start + message) 
            # Receive confirmation
            # If I do not put that, client sends 1000 bytes server reads more than 1000 bytes
            # This is because, when data arrives to server, client completes the next cycle partially and
            # writes some partial data to the message, and server consumes that as well.
            # Another solution is putting a sleep instead of receive.
            # I tried sleep(5) and worked.
            # But I do not like using sleep.
            # So instead, I receive ACK from the server, which means server consumed all the data, then client starts the next cycle. 
            confirmation = s.recv(1) 
    # Be nice and close the file.
    f.close() 
    # Close the socket so that port will not stay open.
    s.close() 

def UDP():
    return 0

def __main__():
    # Do TCP.
    TCP() 
    # DO UDP.
    UDP() 
__main__()