import socket
import struct

# define the server address and port number
#SERVER_ADDRESS = 'attu2.cs.washington.edu'
SERVER_ADDRESS = '127.0.0.1'
PORT = 12235
STEP1 = 1
STEP2 = 2
DIGITS = 887
HEADERSIZE = 12
SERVERPACKAGESIZE = 16
SERVERACKSIZE = 4

def main():
    p1StageA()

def p1StageA():
    # Step a1 set up the UDP connection
    socket_udp = createUDPConnection()
    message = b'hello world'
    # send data to the server
    sendData = createHeaderandPackagePayload(message, 0, STEP1, DIGITS)
    print("Sending packet for Stage A...")
    socket_udp.sendto(sendData, (SERVER_ADDRESS, PORT))
    print("Sent")

    # Step a2
    # receive data from the server
    print("Receiving packet from server...")
    receiveData, server_address = socket_udp.recvfrom(HEADERSIZE + SERVERPACKAGESIZE)
    # Print out message
    print("Received")
    receivedBuffer = struct.unpack("!III I", receiveData[HEADERSIZE:])
    secret = receivedBuffer[3]
    print("Stage A secret: " + str(secret))
    p1StageB(receivedBuffer, socket_udp)

    # close the socket
    socket_udp.close()

def p1StageB(receivedBuffer, socket_udp): 
    num = receivedBuffer[0]
    len = receivedBuffer[1]
    udp_port = receivedBuffer[2]
    secret = receivedBuffer[3]
    i = 0
    print("Sending", num, "packets for Stage B...")
    while i < num :
        #create the payload by creating a package that has the first four bytes as the id and then an empty for the rest of the payload
        payload = bytearray(len + 4)
        int_bytes = struct.pack('!I', i)
        payload[0:4] = int_bytes[0:4]
        #add the header to the payload
        sendData = createHeaderandPackagePayload(payload, secret, STEP1, DIGITS)
        #send data to server
        socket_udp.sendto(sendData, (SERVER_ADDRESS, udp_port))
        receiveData, server_address = socket_udp.recvfrom(HEADERSIZE + SERVERACKSIZE)
        receivedBuffer = struct.unpack("!I", receiveData[HEADERSIZE:])
        if receivedBuffer[0] == i:
            i += 1
    print("Sent all", num, "packets for Stage B.")

    recData, recAddr = socket_udp.recvfrom(HEADERSIZE + 8)
    recBuffer = struct.unpack("!II", recData[HEADERSIZE:])
    tcp_port = recBuffer[0]
    secretB = recBuffer[1]




def createUDPConnection():
    SERVERADDRESS = socket.gethostbyname('attu2.cs.washington.edu')
    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #socket_udp.connect((SERVERADDRESS, PORT))
    return socket_udp

# Need to fill 12 bytes of data before the message as the header
# First 4 bytes is the len of the message
def createHeaderandPackagePayload(payload, secret, step, digits): 
    if len(payload) % 4 == 0 :
        payloadLen = len(payload)
    else : 
        payloadLen = (4 - len(payload) % 4) + len(payload)
    header = struct.pack("!IIHH", len(payload), secret, step, digits)
    return header + payload.ljust(payloadLen, b'\0')

if __name__ == '__main__':
    main()
