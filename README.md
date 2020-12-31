# CENG 435 HW2 - Socket Programming 

# Prepared By
 * Name: Alperen Çaykuş
 * Number: 2237170

# 1- How To Test The Code?

My code can be run as it is shown in the homework PDF. Namely, first run the simulator with the correct parameters. Then, run the server and then run the client with appropriate parameters. An example run would be (Assuming all the files are in the same machine. Otherwise IP must be changed):

```
$ ./simulator 127.0.0.1 127.0.0.1 15595 15596 15591 15593 15594 15597 15598 10 5 3

$ python3 server.py 15593 15594

$ python3 client.py 127.0.0.1 15595 15596 15591 15592
```

>> **IMPORTANT**: 
To close the server side UDP socket, I defined a timeout variable (SERVER_TIMEOUT = 13) in the server code. This means, if no data is received in 13 seconds, server UDP function returns as it thinks the client has terminated. This also means that the all the time prints will be done after at max 13 seconds. 
For those reasons, setting a delay value more than 13 may cause issues in my code. **Hence, the last parameter of simulator must be less than 3.** The server timeout value can be changed by changing the referred variable. Also, server may terminate in less than 13 seconds as explained in section 'Which Problems Did I Face?'

# 2- What Have I Done?

I implemented a server and a client. Both can communicate over TCP and UDP. Client sends a file over the socket and server reconstructs the file. 
Since UDP is a lossy protocol, I also implemented a RDT to make UDP lossless.
As an extra step, for UDP, I used MD5 hash to verify data integrity (i.e, as checksum) since MD5 is a hashing algorithm that is commonly used to determine data integrity.

# 3- Which Part Did I Start With?

I started with TCP as it is easier than UDP because it is already lossless. That means I did not need to implement an RDT so I thought it will be simpler, hence started with it. I first implemented the sockets, but not the data transmission. Then, I implemented some helpers, which encodes-decodes data back so that they can be sent over the socket. 

# 4- How Did I Plan What To Do?

I first read the book and examined the sample codes on the book. Later, I took a pen and paper and decided the protocol that I am going to use. Implementation of TCP was simple as no RDT was needed. Therefore, after creating the protocol, I first coded client side and then the server side for TCP.

However, UDP part was tricky since an RDT was needed. I first determined the RDT as my procotol would change according to the RDT I was going to use. I again took a pen and paper, then first determined the RDT by drawing a finite state machine, and then determined the protocol accordingly.

# 5- Which Problems Did I Face?

I experienced lots of problems. First of all, in TCP, when I do a socket write, I thought that the receiver would receive the same data (i.e, read and write would be symmetric). My first implementation of TCP was returning an ACK to the client so this asymmetric read was not an issue. However, then I realised that the simulator does not support TCP data forwarding from server to client so I deleted this line, and the mentioned asymmetric read error happened. It took me days to debug this and later I learned that this is due to fact that TCP is a streaming protocol, not a messaging protocol. Which means socket reads and writes do not have to be symmetric. Therefore, I implemented a buffer on the server side and the problem was solved. 

In the UDP part, I had problems with closing the UDP socket on server side upon the termination of client. I thought about this for three hours but could not find any solution that does not involve timeout of the server. Then, I contacted with one of our assistants, and he suggested me to do a best-effort algorithm. As suggested by him, on client side, I send the leave message and leave without waiting for a response. If the server receives the packet correctly, then the server terminates as well. If the server does not receive correctly, it keeps listening the socket for new data but as the client is dead, it will not get any data. Eventually, it will time out in SERVER_TERMINATE seconds (defined in server.py) and will be terminated. 

# 6- What Did I Learn After Study?

I did socket programming in other languages as well. However, this was a different experience. For instance, in Java, I never needed to buffer incoming data as Java sockets (at least the ones I used) handle symmetric read and write of sockets. I also have never handled UDP losses before. Therefore, I learned 

* Buffering the incoming TCP data
* Making UDP secure by implementing an RDT.
* Python sockets

# 7- How Many Days Did It Take?

Due to errors I have experienced, this assignment took approximately 7 days. Especially, learning that TCP socket reads may be asymmetric took lots of days as I never encountered this before and could not think of such a thing.

# 8- RDT Protocol I Have Used

I implemented my own but my own implementation is really a variant of RDT 3.0 Stop & Wait. Instead of sending 0 or 1, I sent the corresponding packet number. In my implementation, packet numbers start from 1 and is incremented on each succesful transfer. I treated the packet value 0 as a special case, which represents NAK. The sender sends a packet with protocol [MD5 CHECKSUM : TIMESTAMP : PACKETNUMBER : DATA]. If the data is corrupt, receiver requests the correct packet by sending NAK. If the data is not corrupt, then the packet number is checked if it mathces with the receiver's expected. If it does match, then an ACK is sent with the current packet number. Otherwise, an ACK with the recevied packet's number is sent. The sender keeps sending the same packet until it is ACKed. My implementation really works like RDT 3.0 but instead of 0 - 1, I start packet numbers from 1 and increment it on each successful transfer. My code handles all the possible cases and makes no assumptions about anything. Additionally, client side treats packet number 0 differently as well. Client receiving NAK (i.e, packet 0) means server received a corrupt packet. However, server receiving a NAK (i.e, client sent NAK) is used to indicate that the client is terminating.
