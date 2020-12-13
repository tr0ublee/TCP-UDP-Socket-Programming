'''
    Alperen Caykus
    2237170
'''
import socket
import sys
from datetime import datetime
import time
import struct
import hashlib

# UDP_PORT = sys.argv[1] # read server listening UDP Port.
# TCP_PORT = sys.argv[2] # read server listenin TCP Port.

# Local address to bind.
IP = '127.0.0.1' 
TCP_PORT = 5864
UDP_PORT = 5850
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
# Byte count for packet number
PACKET_NUM_SIZE_IN_BYTES = 1
# Use big endian when necessary
ORDER = 'big'
MD5_ENCODE_TYPE = 'utf-8'
MD5_BYTE_LEN = len(bytes(hashlib.md5(''.encode('utf-8')).hexdigest(), MD5_ENCODE_TYPE))

'''
    Given binary timestamp, converts it to double back and returns it
'''
def getBinaryToTime(bin):
    return struct.unpack("d", bin)[0]

def TCP():
    '''
        Protocol Format: [TIMESTAMP : DATA]
    '''
    # create the socket.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    i = 0
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

def UDP(s):
    '''
       Protocol Format: [TIMESTAMP : MD5 : PACKETNUMBER : DATA]
    '''
    # create the file to write into.
    f = open(UDP_FILENAME, "wb")
    timeStart = 0
    timeEnd = TIME_LENGTH
    checkSumStart = timeEnd
    checkSumEnd = MD5_BYTE_LEN + TIME_LENGTH
    packetNumStart = checkSumEnd
    packetNumEnd = packetNumStart + PACKET_NUM_SIZE_IN_BYTES
    dataStart = packetNumEnd
    while True:
        received, add = s.recvfrom(CHUNK_SIZE)
        end = time.time()
        start = received[timeStart:timeEnd]
        print('Start', start)

        # convert binary timeStamp to double
        start = getBinaryToTime(start)
        checksum = received[checkSumStart : checkSumEnd]
        print('Check', checksum)
        packetNumber = received[packetNumStart : packetNumEnd]
        print('Pack', packetNumber)
        data = received[dataStart:]
        print('Data', data)
        s.sendto(bytes(1), add)



    s.close()
    f.close()
def __main__():
    # create the UDP socket first so that we can directly start UDP after TCP ends.
    sUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # bind to IP and UDP port.
    sUDP.bind((IP, UDP_PORT))


    # Do TCP
    # TCP()
    # DO UDP
    UDP(sUDP)


__main__()