'''
    Alperen Caykus
    2237170
'''
import socket
import sys
from datetime import datetime
import time
import struct

# UDP_PORT = sys.argv[1] # read server listening UDP Port.
# TCP_PORT = sys.argv[2] # read server listenin TCP Port.

# Local address to bind.
IP = '127.0.0.1' 
TCP_PORT = 5856
UDP_PORT = 5855
# Chunk size that is sent by the client. Client sends 1000 bytes, server reads 1000 bytes.
CHUNK_SIZE = 1000 
# Get the length of binary timestamp string. 
TIME_LENGTH = len(struct.pack("d",time.time()))
# file to be read by TCP. 
TCP_FILENAME = "transfer_file_TCP.txt"
# file to be read by UDP. 
UDP_FILENAME = "transfer_file_UDP.txt"
# multiplier to convert s to ms 
MILISEC = 1e3 

'''
    Given binary timestamp, converts it to double back and returns it
'''
def getBinaryToTime(bin):
    return struct.unpack("d", bin)[0]

def TCP():
    # create the socket.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind to IP and port. 
    s.bind((IP , TCP_PORT))
    # start listening 
    s.listen(1)
    # accept connection requests 
    conn , addr = s.accept()
    # create the file to write into.
    f = open(TCP_FILENAME, "wb")
    # an array that holds the time difference values. Will be used to measure total and avg time.
    timeSeries = []
    while True:
        # read CHUNK_SIZE bytes (1000 bytes). 
        # received is in the form timeStamp + actual data
        received = conn.recv(CHUNK_SIZE)
        # get the current time.
        end = time.time() 
        if not received:
            # client is done
            break 
        # extract the timeStamp that the client had sent
        start = received[0:TIME_LENGTH]
        # convert binary timeStamp to double
        start = getBinaryToTime(start)
        # take time differences
        diff = end - start 
        #store the difference
        timeSeries.append(diff) 
        # read the actual data.
        data = received[TIME_LENGTH : ]
        # write data into file.
        f.write(data)
        # send True to client to tell that 'ACK, I received your message' 
        conn.send(bytes(True)) 
    # close the connection.
    conn.close() 
    # close the socket.
    s.close() 
    # close the file
    f.close()
    # accumulator for total transmission time calculation.
    total = 0 
    for i in timeSeries:
        # calculate total
        total += i 
    # print average by sum(array)/array.length in ms
    print("TCP Packets Average Transmission Time: " + str(MILISEC * total/len(timeSeries)) + " ms") # calculate avg in ms
    # print total by sum(array) in ms
    print("TCP Communication Total Transmission Time: " + str(MILISEC * total) + " ms") # calculate total in ms

def UDP():
    # create the socket.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # bind to IP and port. 
    s.bind((IP , UDP_PORT))   
    # create the file to write into.
    f = open(UDP_FILENAME, "wb")
def __main__():
    # Do TCP
    TCP()
    # DO UDP
    UDP()


__main__()