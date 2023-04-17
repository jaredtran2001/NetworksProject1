import socket
import struct
import sys

SERVER_ADDRESS = 'attu2.cs.washington.edu'
LOCALHOST = '127.0.0.1'
PORT = 12235
STEP1 = 1
STEP2 = 2
DIGITS = 887
HEADER_SIZE = 12
SERVER_PACKAGE_SIZE = 16
SERVER_ACK_SIZE_STAGE_B = 4
SERVER_ACK_SIZE_STAGE_C = 13
SERVER_ACK_SIZE_STAGE_D = 4


def main():
    p1_stage_a()
    sys.exit("Part 1 Complete.")


def p1_stage_a():
    print("\nStarting Stage a")
    # create udp socket
    socket_udp = create_udp_socket()
    payload = b'hello world\0'

    # package and send packet to the server
    sendData = package_header_and_payload(payload, 0, STEP1, DIGITS)
    print(f"\tSending UDP packet to {SERVER_ADDRESS} on port {PORT}...")
    socket_udp.sendto(sendData, (SERVER_ADDRESS, PORT))

    # receive packet from the server
    print(f"\tReceiving UDP packet from {SERVER_ADDRESS}... ")
    receiveData, server_address = socket_udp.recvfrom(
        HEADER_SIZE + SERVER_PACKAGE_SIZE)
    receivedBuffer = struct.unpack("!IIII", receiveData[HEADER_SIZE:])
    print("\tPacket contents: ", receivedBuffer[:])
    num = receivedBuffer[0]
    length = receivedBuffer[1]
    udp_port = receivedBuffer[2]
    secret_a = receivedBuffer[3]
    print(f"\t\tnum: {num} \
          \n\t\tlen: {length} \
          \n\t\tudp_port: {udp_port} \
          \n\t\tsecretA: {secret_a}")
    print("STAGE a complete.\n\nStarting STAGE b...\n")
    # pass integers to stage b
    p1_stage_b(receivedBuffer, socket_udp)


def p1_stage_b(receivedBuffer, socket_udp):
    socket_udp.settimeout(0.5)
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
        # print(f"\tpayload {i}: {payload}\n")

        # add the header to the payload
        sendData = package_header_and_payload(
            payload, secret, STEP1, DIGITS)

        # send data to server
        print(
            f"\tSending UDP packet to {SERVER_ADDRESS} on port {udp_port}...")
        socket_udp.sendto(sendData, (SERVER_ADDRESS, udp_port))

        try:
            # receive data from server
            print(f"\tReceiving packet {i} from {SERVER_ADDRESS}... \n")
            receiveData, server_address = socket_udp.recvfrom(
                HEADER_SIZE + SERVER_ACK_SIZE_STAGE_B)
            receivedBuffer = struct.unpack("!I", receiveData[HEADER_SIZE:])
            if receivedBuffer[0] == i:
                i += 1
        except socket.timeout:
            print(f"\tRetrying... \n")
            continue

    recData, recAddr = socket_udp.recvfrom(HEADER_SIZE + 8)
    recBuffer = struct.unpack("!II", recData[HEADER_SIZE:])
    tcp_port = recBuffer[0]
    secretB = recBuffer[1]
    print(f"\tTCP port from STAGE b is: {tcp_port}")
    print(f"\tSecret from STAGE b is: {secretB}\n")
    socket_tcp = create_tcp_socket(SERVER_ADDRESS, tcp_port)
    socket_udp.close()
    print("STAGE b complete.\n\nStarting STAGE c...\n")
    p1_stage_c(recBuffer, socket_tcp)


def p1_stage_c(recBuffer, socket_tcp):
    tcp_port = recBuffer[0]
    secretB = recBuffer[1]

    # receive data from the server
    print(
        f"\tReceving TCP packet from {SERVER_ADDRESS} on port {tcp_port}...")
    recData = socket_tcp.recv(HEADER_SIZE + SERVER_ACK_SIZE_STAGE_C)
    recBuffer = struct.unpack("!IIIc", recData[HEADER_SIZE:])
    print(f"\tPacket contents: {recBuffer[:]}")
    num2 = recBuffer[0]
    len2 = recBuffer[1]
    secretC = recBuffer[2]
    c = recBuffer[3]
    print(f"\t\tnum2: {num2} \
          \n\t\tlen2: {len2} \
          \n\t\tsecretC: {secretC} \
          \n\t\tc: {c}")
    print("STAGE c complete.\n\n")
    p1_stage_d(recBuffer, socket_tcp, tcp_port)


def p1_stage_d(recBuffer, socket_tcp, tcp_port):
    # Step d1. The clients sends num2 payloads, each payload of length len2,
    # and each payload containing all bytes set to the character c.
    num2 = recBuffer[0]
    len2 = recBuffer[1]
    secretC = recBuffer[2]
    c = recBuffer[3]
    socket_tcp.settimeout(3)

    i = 0
    while i < num2:
        payload = c.decode() * len2
        payload = payload.encode()
        int_bytes = struct.pack('!%ds' % len2, payload)

        # add the header to the payload
        sendData = package_header_and_payload(
            int_bytes, secretC, STEP1, DIGITS)

        # send data to server
        if i == 0:
            print(f"\tPacket being sent to server {num2} times: {sendData}\n")
        print(
            f"\tSending TCP packet to {SERVER_ADDRESS} on port {tcp_port}...")
        socket_tcp.sendto(sendData, (SERVER_ADDRESS, tcp_port))
        i += 1

    # server seems to respond first with 3 bytes of character c
    # then with header + payload containing secretD
    # iff it received num2 correct payloads first
    for i in range(2):
        try:
            print(f"\tReceving TCP packet from"
                  + f" {SERVER_ADDRESS} on port {tcp_port}...")
            recData = socket_tcp.recv(HEADER_SIZE + SERVER_ACK_SIZE_STAGE_D)
            print(f"\tPacket contents: {recData}")
            if recData == b'':
                break
        except socket.timeout:
            print(f"\tRetrying... \n")
            continue
    recBuffer = struct.unpack("!I", recData[HEADER_SIZE:])
    print(f"\tsecretD is: {recBuffer[0]}")
    print("STAGE d complete.\n\n")
    socket_tcp.close()


def create_tcp_socket(addr, port):
    """Creates TCP socket and gets addr info."""
    SERVERADDRESS = socket.gethostbyname('attu2.cs.washington.edu')
    socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_tcp.connect((addr, port))
    return socket_tcp


def create_udp_socket():
    """"Creates UDP socket and gets addr info."""
    SERVERADDRESS = socket.gethostbyname('attu2.cs.washington.edu')
    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # socket_udp.connect((SERVERADDRESS, PORT))
    return socket_udp


def package_header_and_payload(payload, secret, step, digits):
    """Creates the 12-byte header and padded payload packet."""
    payload_len = len(payload)
    header = struct.pack("!IIHH", payload_len, secret, step, digits)
    return header + payload.ljust(pad_length(payload), b'\0')


def pad_length(payload):
    """Computes padding needed for payload to be 4-byte aligned."""
    if len(payload) % 4 == 0:
        payload_len = len(payload)
    else:
        payload_len = (4 - len(payload) % 4) + len(payload)
    return payload_len


if __name__ == '__main__':
    main()
