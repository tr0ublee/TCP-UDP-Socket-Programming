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

UDP_PORT = int(sys.argv[1]) # read server listening UDP Port.
TCP_PORT = int(sys.argv[2]) # read server listenin TCP Port.

# Local address to bind.
IP = '127.0.0.1' 
# TCP_PORT = 5864
# UDP_PORT = 5850
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
# Use big endian when necessary

'''
    Given binary timestamp, converts it to double back and returns it
'''
def getBinaryToTime(bin):
    # print(struct.unpack("d", bin))
    return struct.unpack("d", bin)[0]

def printTime(arr, type):
    total = 0
    global MILISEC
    for i in arr:
        # calculate total
        total += i
    # print average by sum(array)/array.length in ms
    print(type + " Packets Average Transmission Time: " + str(MILISEC * total/len(arr)) + " ms") # calculate avg in ms
    # print total by sum(array) in ms
    print(type + " Communication Total Transmission Time: " + str(MILISEC * total) + " ms") # calculate total in ms

def TCP():
    '''
        Protocol Format: [TIMESTAMP : DATA]
    '''
    # create the socket.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind to IP and port. 
    s.bind((IP , TCP_PORT))
    # start listening 
    s.listen(1)
    # accept connection requests 
    conn , addr = s.accept()
    # create the file to write into.
    f = open(TCP_FILENAME, "wb+")
    # an array that holds the time difference values. Will be used to measure total and avg time.
    timeSeries = []
    buff = ''.encode(MD5_ENCODE_TYPE)

    num = 0
    while True:
        while len(buff) < CHUNK_SIZE:
            read = conn.recv(CHUNK_SIZE - len(buff))
            if not read:
                break
            buff += read
        end = time.time() 
        if not buff:
            # client and server is done
            break
        # buff = buff[CHUNK_SIZE:]
        received = buff
        buff = ''.encode(MD5_ENCODE_TYPE)
        # extract the timeStamp that the client had sent
        start = received[0:TIME_LENGTH]
        # print('Start ', start)
       
        # convert binary timeStamp to double
        start = getBinaryToTime(start)
        # print(num ,start)
        num += 1

        # print('Endss ', end)
        # take time differences
        diff = end - start 
        # print('Diffs', diff)
        #store the difference
        timeSeries.append(diff) 
        # read the actual data.
        data = received[TIME_LENGTH : ]
        # write data into file.
        f.write(data)
        # send True to client to tell that 'ACK, I received your message' 
        # conn.send(bytes(True))
    # close the connection.
    conn.close() 
    # close the socket.
    s.close() 
    # close the file
    f.close()
    printTime(timeSeries, 'TCP')

'''
    UDP STARTS
    UDP CONSTANTS
'''

ORDER = 'big'
MD5_ENCODE_TYPE = 'utf-8'
MD5_BYTE_LEN = len(bytes(hashlib.md5(''.encode('utf-8')).hexdigest(), MD5_ENCODE_TYPE))

PACKET_NUM_SIZE_IN_BYTES = 8
CHKSUM_START = 0
CHKSUM_END = MD5_BYTE_LEN 
TIME_START = CHKSUM_END
TIME_END = CHKSUM_END + TIME_LENGTH
PACKG_NUM_START = TIME_END
PACKG_NUM_END = PACKG_NUM_START + PACKET_NUM_SIZE_IN_BYTES
DATA_START = PACKG_NUM_END
ACK = [0, 1] #ACK0, ACK1
NACK = 2



def getChecksum(hex):
    return hex.decode(MD5_ENCODE_TYPE)

def getArrivedDataMD5(received):
    return hashlib.md5(received).hexdigest()

def doCheckSum(received):
    try:
        checksum = getChecksum(received[CHKSUM_START : CHKSUM_END])
        arrivedMD5 = getArrivedDataMD5(received[CHKSUM_END:])
    except (UnicodeDecodeError,IndexError):
        return False
    if checksum == arrivedMD5:
        return True
    return False

def getPacketNum(received):
    hex =  received[PACKG_NUM_START : PACKG_NUM_END]
    return int.from_bytes(hex, ORDER)

def makeACK(packet):
    msg = packet.to_bytes(PACKET_NUM_SIZE_IN_BYTES, ORDER)
    msg += bytes(hashlib.md5(msg).hexdigest(), MD5_ENCODE_TYPE)
    # print(msg)
    return msg

def UDP():
    '''
       Protocol Format: [MD5 : TIMESTAMP : PACKETNUMBER : DATA]
    '''
    # create the file to write into.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # bind to IP and UDP port.
    s.bind((IP, UDP_PORT))
    f = open(UDP_FILENAME, "wb+")
    timeSeries = []
    prev = None
    read = []
    expecting = 1
    while True:
        try:
            s.settimeout(12)
            received, add = s.recvfrom(CHUNK_SIZE)
        except socket.timeout:
            s.settimeout(None)
            break
        end = time.time()
        notCorrupt = doCheckSum(received)
        if notCorrupt:
            gotPacket = getPacketNum(received)
            if expecting == gotPacket:
                start = getBinaryToTime(received[TIME_START : TIME_END])
                diff = end - start
                # store the difference
                timeSeries.append(diff)
                # read the actual data.
                data = received[DATA_START:]
                # write data into file.
                read.append(received)
                f.write(data)
                msg = makeACK(expecting)
                s.sendto(msg, add)
                expecting += 1
            else:
                msg = makeACK(gotPacket)
                s.sendto(msg, add)
        else:
            msg = makeACK(0)
            s.sendto(msg, add)
    total  = 0
    for i in range(len(read)):
        for j in range(len(read)):
            if i != j:
                if read[i] == read[j]:
                    print(i, j)
    print(total)
    printTime(timeSeries, 'UDP')
    s.close()
    f.close()
def __main__():
    # create the UDP socket first so that we can directly start UDP after TCP ends.


    print('TCP Started')

    # Do TCP
    TCP()
    print('TCP Ended')

    # DO UDP
    print('UDP Started')

    UDP()
    print('UDP Ended')



__main__()