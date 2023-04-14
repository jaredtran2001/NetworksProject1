import socket
import struct

# define the server address and port number
SERVER_ADDRESS = 'attu2.cs.washington.edu'
PORT = 12235
STEP1 = 1
STEP2 = 2
DIGITS = 887
HEADERSIZE = 12
SERVERPACKAGESIZE = 16

def main():
    p1StageA()

def p1StageA():
    # Step a1 set up the UDP connection
    socket_udp = createUDPConnection()
    message = b'hello world'
    # send data to the server
    sendData = createHeader(message, 0, STEP1, DIGITS)
    socket_udp.sendto(sendData, (SERVER_ADDRESS, PORT))

    # Step a2
    # receive data from the server
    receiveData, server_address = socket_udp.recvfrom(HEADERSIZE + SERVERPACKAGESIZE)
    # Print out message
    receivedBuffer = struct.unpack("!III I", receiveData[HEADERSIZE:])
    secret = receivedBuffer[3]
    print("Stage A secret: " + str(secret))
    # close the socket
    socket_udp.close()

def createUDPConnection():
    SERVERADDRESS = socket.gethostbyname('attu2.cs.washington.edu')
    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_udp.connect((SERVERADDRESS, PORT))
    return socket_udp

# Need to fill 12 bytes of data before the message as the header
# First 4 bytes is the len of the message
def createHeader(payload, secret, step, digits):
    payloadLen; 
    if len(payload) % 4 == 0 :
        payloadLen = len(payload)
    else : 
        payloadLen = (4 - len(payload) % 4) + len(payload)
    header = struct.pack("!IIHH", len(payload), secret, step, digits)
    return header + payload.ljust(payloadLen, b'\0')

if __name__ == '__main__':
    main()
