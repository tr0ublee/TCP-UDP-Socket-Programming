'''
    Alperen Caykus
    2237170
'''
import socket
import sys
import time
import struct
import hashlib

UDP_PORT = int(sys.argv[1]) # read server listening UDP Port.
TCP_PORT = int(sys.argv[2]) # read server listenin TCP Port.

# Address to bind.
IP = '' 
# Chunk size that is sent by the client. Client sends 1000 bytes, server reads 1000 bytes.
CHUNK_SIZE = 1000 
# Get the size of timestamps in bytes
TIME_LENGTH = len(struct.pack("d",time.time()))
# file to be written on by TCP. 
TCP_FILENAME = "transfer_file_TCP.txt"
# multiplier to convert s to ms 
MILISEC = 1e3

'''
    Given binary timestamp, converts it to double back and returns it
'''
def getBinaryToTime(bin):
    return struct.unpack("d", bin)[0]
'''
    Given time array, returns avg
'''
def getAvgTime(arr):
    global MILISEC
    if len(arr) == 0:
        return 0
    total = 0
    for i in arr:
        # calculate total
        total += i
    return MILISEC * total/len(arr)

def TCP():
    '''
        Protocol Format: [TIMESTAMP : DATA]
    '''
    # create the socket.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # I put the following line because whenever I restart the client code, 
    # although I close the socket, the connection was refused,
    # stating that Address already in use.
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
    # Since TCP is a stream, reads and writes onto socket can be asymmetric.
    # I personally experienced this where client was sending less data than it wass supposed to send
    # because it was sending some chunks in the previous iteration.
    # To solve this, I first sent ACK from server to client, but since simulator does not support this
    # I needed to remove it and implemented a buffer.
    buff = ''.encode(MD5_ENCODE_TYPE)
    # A boolean to differentatie first time stamp from the other time stamps.
    getFirst = True
    # holds the first time stamp.
    first = 0
    # holds the last time stamp.
    last = 0
    while True:
        while len(buff) < CHUNK_SIZE:
            # read the socket until buffer size becomes 1000 bytes (CHUNK SIZE)
            # The reasoin is already explained.
            read = conn.recv(CHUNK_SIZE - len(buff))
            if not read:
                # no data arrived, client is done.
                break
            buff += read
        # measure the current time.
        end = time.time()
        # save the last measured timestamp.
        last = end 
        if not buff:
            # client and server is done
            # terminate.
            break
        # start consuming the buffer
        received = buff
        # reset the buffer.
        buff = ''.encode(MD5_ENCODE_TYPE)
        # extract the timeStamp that the client had sent
        start = received[0:TIME_LENGTH]
        # convert binary timeStamp to double
        start = getBinaryToTime(start)
        if getFirst:
            # first packet arrived. 
            # Save its timestamp to calculate total time.
            getFirst = False
            first = start
        # take time differences (i.e, time taken by the packet)
        diff = end - start 
        #store the difference
        timeSeries.append(diff) 
        # read the actual data.
        data = received[TIME_LENGTH : ]
        # write data into file.
        f.write(data)
    # close the connection.
    conn.close() 
    # close the socket.
    s.close() 
    # close the file
    f.close()
    global MILISEC
    total = last - first
    total = MILISEC * total
    # return avg transmission time
    return getAvgTime(timeSeries), total 

'''
    UDP STARTS
'''
# Use big endian when encoding the integers
ORDER = 'big'
# Use UTF-8 when encoding strings (since MD5 is also represented as a string)
MD5_ENCODE_TYPE = 'utf-8'
# Size of an encoded MD5. I use that in my protocol as index when accessing MD5.
MD5_BYTE_LEN = len(bytes(hashlib.md5(''.encode('utf-8')).hexdigest(), MD5_ENCODE_TYPE))
# file to be read by UDP. 
UDP_FILENAME = "transfer_file_UDP.txt"
# Byte count for packet number.  I use that in my protocol as index when accessing packet number
PACKET_NUM_SIZE_IN_BYTES = 8
# Index that indicates start position of MD5 in my protocol.
CHKSUM_START = 0
# Index that indicates end position of MD5 in my protocol.
CHKSUM_END = MD5_BYTE_LEN 
# Index that indicates start position of timestamp in my protocol.
TIME_START = CHKSUM_END
# Index that indicates end position of timestamp in my protocol.
TIME_END = CHKSUM_END + TIME_LENGTH
# Index that indicates start position of package number in my protocol.
PACKG_NUM_START = TIME_END
# Index that indicates end position of package number in my protocol.
PACKG_NUM_END = PACKG_NUM_START + PACKET_NUM_SIZE_IN_BYTES
# Index that indicates start position of actual data in my protocol.
DATA_START = PACKG_NUM_END
# special NACK value. Since in my implementation, packet numbers start from 1, I chose 0 to be a special value.
# I explain NACK in client core in more details.
NACK = 0
# terminate server in SERVER_TERMINATE seconds if no message arrives
SERVER_TERMINATE = 13

'''
    Given an MD5 in hex, convert it to string MD5
'''
def getChecksum(hex):
    return hex.decode(MD5_ENCODE_TYPE)
'''
    Get the MD5 of received packet
'''
def getArrivedDataMD5(received):
    return hashlib.md5(received).hexdigest()
'''
    A function that checks if the received packet is corrupt or not.
'''
def doCheckSum(received):
    try:
        # Get the checksum value in the received packet
        checksum = getChecksum(received[CHKSUM_START : CHKSUM_END])
        # Get the checksum of received in the received packet.
        # Exclude MD5 part as MD5 in the packet encodes timestamp, data and packet number.
        # This is also explained in client.
        arrivedMD5 = getArrivedDataMD5(received[CHKSUM_END:])
    except (UnicodeDecodeError,IndexError):
        '''
            Either something is not in order or length does not match.
            So, smth is corrupted.
        '''
        return False
    if checksum == arrivedMD5:
        # Not corrupt.
        return True
    # Corrupt again.
    return False
'''
    Given received packet, extracts the packet number and returns it in integer.
'''
def getPacketNum(received):
    hex =  received[PACKG_NUM_START : PACKG_NUM_END]
    return int.from_bytes(hex, ORDER)
'''
    Given packet number, creates the ACK message for that.
    returns in the format [ACKnumber + MD5 of ACKnumber]
    Directly can be sent over the socket.
'''
def makeACK(packet):
    msg = packet.to_bytes(PACKET_NUM_SIZE_IN_BYTES, ORDER)
    msg += bytes(hashlib.md5(msg).hexdigest(), MD5_ENCODE_TYPE)
    return msg

def UDP():
    '''
       Protocol Format: [MD5 : TIMESTAMP : PACKETNUMBER : DATA]
    '''
    # create the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # bind to IP and UDP port.
    s.bind((IP, UDP_PORT))
    # open file to write received data.
    f = open(UDP_FILENAME, "wb+")
    # store time differences to calculate the avg time.
    timeSeries = []
    # Indicates which packet the server is expecting.
    expecting = 1
    # A boolean to differentatie first time stamp from the other time stamps.
    getFirst = True
    # holds the first time stamp.
    first = 0
    # holds the last time stamp.
    last = 0
    while True:
        s.settimeout(SERVER_TERMINATE)
        try:
            # receive 1000 bytes
            received, add = s.recvfrom(CHUNK_SIZE)
            s.settimeout(None)
        except socket.timeout:
            # No message arrived in SERVER_TERMINATE seconds.
            # Client must have been terminated.
            # Terminate the server process
            s.settimeout(None)
            break
        s.settimeout(None)
        # get the current time stamp.
        end = time.time()
        # set the last to current so that 
        # when this loop exits, last holds the last timestamp.
        last = end
        # check if the received packet is corrupt or not.
        notCorrupt = doCheckSum(received)
        if notCorrupt:
            # extract the packet information.
            gotPacket = getPacketNum(received)
            # get the timestamp of the packet.
            start = getBinaryToTime(received[TIME_START : TIME_END])
            if getFirst:
                # first packet arrived. get its timestamp.
                getFirst = False
                # store it.
                first = start
            # calculate the time difference.
            diff = end - start
            if expecting == gotPacket:
                # got the packet I was expecting.
                # store the difference
                timeSeries.append(diff)
                # read the actual data.
                data = received[DATA_START:]
                # write data into file.
                f.write(data)
                # create ACK for packet #expecting.
                msg = makeACK(expecting)
                # send the ACK.
                s.sendto(msg, add)
                # start expecting the next chunk.
                expecting += 1
            elif gotPacket == NACK:
                # NACK is used special here.
                # Client sent NACK, which means client sent all the packets and now it is going to terminate.
                # terminate server as well.
                break
            else:
                '''
                    Server is ahead of client. Client thinks server did not get the previous packet.
                    Inform client that previous packet was correct.
                    Update the timestamp as PDF says so.
                '''
                timeSeries.pop()
                timeSeries.append(diff)
                msg = makeACK(gotPacket)
                s.sendto(msg, add)
        else:
            '''
                Received a corrupt packet. Send NACK and request the same packet again.
            '''
            msg = makeACK(NACK)
            # send the NACK.
            s.sendto(msg, add)
    # close the socket.
    s.close()
    # close the file
    f.close()
    total = last - first
    global MILISEC
    total = MILISEC * total
    # return avg time and total
    return getAvgTime(timeSeries), total
def __main__():
    global MILISEC
    # Do TCP
    tcpAvg, tcpTotal = TCP()
    # DO UDP
    udpAvg, udpTotal = UDP()
    # print averages
    print("TCP Packets Average Transmission Time: " + str(tcpAvg) + " ms") # calculate avg in ms
    print("UDP Packets Average Transmission Time: " + str(udpAvg) + " ms") # calculate avg in ms
    # print totals
    print("TCP Communication Total Transmission Time: " + str(tcpTotal) + " ms") # calculate total in ms
    print("UDP Communication Total Transmission Time: " + str(udpTotal) + " ms") # calculate total in ms

__main__()