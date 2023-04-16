import socket
import struct

SERVER_ADDRESS = 'attu2.cs.washington.edu'
LOCALHOST = '127.0.0.1'
PORT = 12235
STEP1 = 1
STEP2 = 2
DIGITS = 887
HEADERSIZE = 12
SERVERPACKAGESIZE = 16
SERVERACKSIZE = 4


def main():
    p1_stage_a()


def p1_stage_a():
    # create udp socket
    socket_udp = create_udp_socket()
    payload = b'hello world'

    # package and send packet to the server
    sendData = package_header_and_payload(payload, 0, STEP1, DIGITS)
    print(f"\tSending UDP packet to {SERVER_ADDRESS} on port {PORT}...")
    socket_udp.sendto(sendData, (SERVER_ADDRESS, PORT))
    print("\tSent")

    # receive packet from the server
    print(f"\tReceiving packet from {SERVER_ADDRESS}... ")
    receiveData, server_address = socket_udp.recvfrom(
        HEADERSIZE + SERVERPACKAGESIZE)
    receivedBuffer = struct.unpack("!IIII", receiveData[HEADERSIZE:])
    print("\tPacket contents: ", receivedBuffer[:])
    num = receivedBuffer[0]
    length = receivedBuffer[1]
    udp_port = receivedBuffer[2]
    secret_a = receivedBuffer[3]
    print(f"\t\tnum: {num} \
          \n\t\tlen: {length} \
          \n\t\tudp_port: {udp_port} \
          \n\t\tsecretA: {secret_a}")

    # pass integers to stage b
    p1_stage_b(receivedBuffer, socket_udp)
    socket_udp.close()


def p1_stage_b(receivedBuffer, socket_udp):
    print("\tSTAGE a complete.\n\tStarting STAGE b...\n")
    num = receivedBuffer[0]
    len = receivedBuffer[1]
    udp_port = receivedBuffer[2]
    secret = receivedBuffer[3]
    i = 0
    while i < num:
        # create the payload by creating a package that has the first four
        # bytes as the id and then an empty for the rest of the payload
        payload = bytearray(len + 4)
        int_bytes = struct.pack('!I', i)
        payload[0:4] = int_bytes[0:4]
        print(f"\tpayload {i}: {payload}\n")

        # add the header to the payload
        sendData = package_header_and_payload(
            payload, secret, STEP1, DIGITS)

        # send data to server
        print(
            f"\tSending UDP packet to {SERVER_ADDRESS} on port {udp_port}...")
        socket_udp.sendto(sendData, (SERVER_ADDRESS, udp_port))

        # receive data from server
        print(f"\tReceiving packet from {SERVER_ADDRESS}... ")
        receiveData, server_address = socket_udp.recvfrom(
            HEADERSIZE + SERVERACKSIZE)
        receivedBuffer = struct.unpack("!I", receiveData[HEADERSIZE:])
        if receivedBuffer[0] == i:
            i += 1

    recData = socket_udp.recvfrom(HEADERSIZE + 8)
    recBuffer = struct.unpack("!II", recData[HEADERSIZE:])
    tcp_port = recBuffer[0]
    secretB = recBuffer[1]


def create_udp_socket():
    """"Creates UDP socket and gets addr info."""
    SERVERADDRESS = socket.gethostbyname('attu2.cs.washington.edu')
    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # socket_udp.connect((SERVERADDRESS, PORT))
    return socket_udp


def package_header_and_payload(payload, secret, step, digits):
    """Creates the 12-byte header and padded payload packet."""
    payload_len = pad_length(payload)
    header = struct.pack("!IIHH", payload_len, secret, step, digits)
    return header + payload.ljust(payload_len, b'\0')


def pad_length(payload):
    """Computes padding needed for payload to be 4-byte aligned."""
    if len(payload) % 4 == 0:
        payload_len = len(payload)
    else:
        payload_len = (4 - len(payload) % 4) + len(payload)
    return payload_len


if __name__ == '__main__':
    main()
