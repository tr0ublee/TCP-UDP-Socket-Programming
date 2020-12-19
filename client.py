'''
    Alperen Caykus
    2237170
'''
import socket
import sys
import time
import struct
import hashlib

# read server ip
SERVER_IP = sys.argv[1]
# read UDP server listening port 
UDP_SERVER_PORT = int(sys.argv[2])
# read TCP server listening port 
TCP_SERVER_PORT = int(sys.argv[3])
# read UDP client sending port 
UDP_CLIENT_PORT = int(sys.argv[4])
# read TCP client sending port
TCP_CLIENT_PORT = int(sys.argv[5])

# Get the size of timestamps in bytes
TIME_SIZE_IN_BYTES = len(struct.pack("d",time.time()))
# Chunk size in bytes. 
CHUNK_SIZE = 1000 
# file to be sent by TCP.
TCP_FILENAME = "transfer_file_TCP.txt"


'''
    A function that returns timestamps in binary.
'''
def getBinaryTimeStamp():
    start = time.time()
    return struct.pack("d", start)

def TCP():
    '''
        PROTOCOL: [TIMESTAMP | MESSAGE]
    '''
    # create the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # I put the following line because whenever I restart the client code, 
    # although I close the socket, the connection was refused,
    # stating that Address already in use.
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    # Set client's port and bind.
    s.bind(('', TCP_CLIENT_PORT)) 
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
            s.send(start + message)
    # Be nice and close the file.
    f.close() 
    # Close the socket so that port will not stay open.
    s.close() 

'''
    UDP STARTS
''' 
# file to be sent by UDP.
UDP_FILENAME = "transfer_file_UDP.txt" 
'''
    Variables for protocol boundaries as I use a fixed-length protocol
'''
# Byte count for packet number.  I use that in my protocol as index when accessing packet number
PACKET_NUM_SIZE_IN_BYTES = 8
# Use big endian when encoding the integers
ORDER = 'big'
# Use UTF-8 when encoding strings (since MD5 is also represented as a string)
MD5_ENCODE_TYPE = 'utf-8'
# Size of an encoded MD5. I use that in my protocol as index when accessing MD5.
MD5_BYTE_SIZE = len(bytes(hashlib.md5(''.encode('utf-8')).hexdigest(), MD5_ENCODE_TYPE))
# timeout value
TIMEOUT = 1 
# special NACK value. Since in my implementation, packet numbers start from 1, I chose 0 to be a special value.
NACK = 0

'''
    Given data and packet number, that function produces an output in the form
    [MD5 : TIMESTAMP : PACKETNUMBER : DATA] that can directly be sent over the socket.
    Note that MD5 hashes the timestamp + packetnumber + data part.
'''
def makeMsg(data, packet):
    packetNum = packet.to_bytes(PACKET_NUM_SIZE_IN_BYTES, ORDER)
    start = getBinaryTimeStamp()
    tmp = start + packetNum + data
    checksum = bytes(hashlib.md5(tmp).hexdigest(), MD5_ENCODE_TYPE)
    message = checksum + start + packetNum + data
    return message

def UDP():
    '''
        PROTOCOL: [MD5 : TIMESTAMP : PACKETNUMBER : DATA]
    '''
    # create the socket 
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Set client's port and bind.
    s.bind(('', UDP_CLIENT_PORT))
    # create the destination Tupple, which contains server's listening UDP port and server IP.
    sendAddress = (SERVER_IP, UDP_SERVER_PORT)
    # read CHUNK_SIZE - TIMESIZE - PACKET NUM - CHECKSUM bytes from disk
    readSize = CHUNK_SIZE - TIME_SIZE_IN_BYTES - PACKET_NUM_SIZE_IN_BYTES - MD5_BYTE_SIZE
    # first packet that will be sent
    packet = 1
    # counter that holds number of resent packets.
    resent = 0
    # a state indircator if the client is done or not.
    isExiting = False
    with open(UDP_FILENAME, 'rb') as f:
        while True:
            # read data with size CHUNK_SIZE - TIMESIZE - PACKET NUM - CHECKSUM bytes from disk 
            data = f.read(readSize)
            if not data:
                # EOF. Set state to exiting.
                isExiting = True
                # Use NACK as BYE message. 
                # When client sends NACK, it means client is leaving.
                # When server sends NACK, it means the data sent from client was corrupted.
                packet = NACK
                # Padding for BYE message.
                data = bytes(readSize)
            # read packet is not acked.
            acked = False
            # should send indicates if the client should do a listen or send.
            # when delays arrive, we should discard them and wait for the actual message. 
            # So, we dont need to send the message again. This variable handles this.
            shouldSend = True
            while not acked:
                # Loop until packet is acked.
                if shouldSend:
                    # Either clients sends it first message 
                    # or client receives corrupted ACK or
                    # client times out or
                    # server receives corrupted data or
                    # a packet is lost.
                    # Send the message. 
                    msg = makeMsg(data, packet)
                    s.sendto(msg, sendAddress)
                # start the timer
                s.settimeout(TIMEOUT)
                try:
                    if isExiting:
                        # best effort as suggested by one of our TA.
                        # client sends it termination message and leaves without caring if the server received or not.
                        # If server does not receive, server will terminate by timing out.
                        s.settimeout(None)
                        break
                    # recaive data in the format [ACKnum + MD5 OF PACKET]
                    res = s.recv(MD5_BYTE_SIZE + PACKET_NUM_SIZE_IN_BYTES)
                    # clear the timer
                    s.settimeout(None)
                    # get the ACKnum
                    ackNum = res[0:PACKET_NUM_SIZE_IN_BYTES]
                    # get the MD5 part of the received packet
                    echoMD5 = res[PACKET_NUM_SIZE_IN_BYTES: MD5_BYTE_SIZE + PACKET_NUM_SIZE_IN_BYTES]
                    # rehash ackNum to check if received packet is corrupted.
                    ackMD5 = bytes(hashlib.md5(ackNum).hexdigest(), MD5_ENCODE_TYPE)
                    # convert acknum to int to be more user friendly.
                    ackNum = int.from_bytes(ackNum, ORDER)
                    if ackMD5 == echoMD5:                 
                        # received packet is not corrupted.  
                        if packet == ackNum:
                            # transmitted the current packet correctly. Move.
                            # set shouldSend just in case as now we will send the next packet.
                            shouldSend = True
                            # received acknowledgement. Set it to break the loop.
                            acked = True
                            # Set packet to next packet.
                            packet += 1
                        # As I said, when server sends NACK, it means server received corrupt data.
                        elif ackNum == NACK:
                            # increment counter and set shouldSend to send the same packet again.
                            resent += 1
                            shouldSend = True
                        else:
                            # A previously delayed packet arrived. Discard it. Keep listening to socket.
                            # Dont send new data since server might be sending an answer.
                            shouldSend = False
                    else:
                        # client received a corrupt packet.
                        # Send the same data just in case client received a corrupt packet as well.
                        # resend the packet in case the server received bad data as well.
                        resent += 1
                        shouldSend = True
                except (UnicodeDecodeError,TypeError, IndexError, socket.timeout):
                    s.settimeout(None)
                    # Client did not receive any message and timer interrupt occured or packet was corrupt and 
                    # parse failed . Resend the same packet in case the packet is lost.
                    resent += 1
                    shouldSend = True
            if isExiting:
                # Byee
                break   
            s.settimeout(None)
  
    # print resent packets.
    print('UDP Transmission Re-transferred Packets: ' + str(resent))
    # Be nice and close the file.
    f.close() 
    # Close the socket so that port will not stay open.
    s.close() 
    return 0

def __main__():
    # Do TCP.
    TCP()
    # DO UDP.
    UDP()
# Call main
__main__()