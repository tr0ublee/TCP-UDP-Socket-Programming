import socket
import sys
import time

'''
SERVER_IP = sys.argv[1] # read server ip
UDP_SERVER_PORT = sys.argv[2] # read UDP server listening port
TCP_SERVER_PORT = sys.argv[3] # read TCP server listening port
UDP_CLIENT_PORT = sys.argv[4] # read UDP client sending port
TCP_CLIENT_PORT = sys.argv[5] # read TCP client sending port
'''

SERVER_IP = '127.0.0.1'
TCP_SERVER_PORT = 5858
TCP_CLIENT_PORT = 2755 

CHUNK_SIZE = 1000 # Chunk size in bytes.
TCP_FILENAME = "transfer_file_TCP.txt" # file to be sent by TCP.
UDP_FILENAME = "transfer_file_UDP.txt" # file to be sent by UDP.
MILISEC = 1e3 # multiplier to convert s to ms

def TCP():
    # an array that is going to hold time difference values between 
    # the sent packet and arrival of that packet to the server.
    timeArray = [] 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create the socket.
    # I put the following line because whenever I restart the client code, 
    # although I close the socket, the connection was refused,
    # stating that Address already in use. I learned that this is 
    # due to the fact that the socket is left in the TCP TIME-WAIT state.
    # The following line solves that.
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    s.bind((SERVER_IP, TCP_CLIENT_PORT)) # Set client's port and bind socket to SERVER_IP and TCP_CLIENT_PORT.
    s.connect((SERVER_IP, TCP_SERVER_PORT))  # Connect to server with ip SERVER_IP and listening the port TCP_SERVER_PORT
    with open(TCP_FILENAME, 'rb') as f: # read binary TCP file.
        while True:
            message = f.read(CHUNK_SIZE) # read READ_SIZE (1000) bytes.
            if not message: #  Reached to eof. We are done.
                break
            start = time.time() # start measuring
            s.send(message) # Send the message that is read from the disk.
            confirmation = s.recv(1) # Receive confirmation
            end = time.time() # end measuring
            timeArray.append(end - start) # save the time measurement.
             # convert confirmation to bool as server sends True. 
             # Not necessary to do that, just for fun.
            confirmation = bool(confirmation)
    s.close() # Be nice and close the socket so that port will not stay open.
    total = 0 # accumulator for total transmission time calculation.
    for i in timeArray:
        total += i # calculate total
    print("TCP Packets Average Transmission Time: " + str(MILISEC * total/len(timeArray)) + " ms") # calculate avg in ms
    print("TCP Communication Total Transmission Time: " + str(MILISEC * total) + " ms") # calculate total in ms

def UDP():
    return 0

def __main__():
    TCP() # Do TCP.
    UDP() # DO UDP.


__main__()