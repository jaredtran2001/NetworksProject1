from part1.Part1 import *
import socket
import struct
import threading
import random

BUFFERSIZE = 1024

def p2StageA(s, client_data, client_adddr):
    while True:
        # receive packet from client
        header_data = client_data[:HEADERSIZE]
        header_data = struct.unpack('!IIHH', header_data)
        # verify header data
        if header_data != [11, 0, STEP1, DIGITS]:
            print("Incorrect header")
        # verify payload
        payload_len = header_data[0]
        client_payload = client_data[HEADERSIZE:payload_len]
        if client_payload != b'hello world':
            print("Incorrect message payload from client")

        # randomly generate num, len, udp_port, and secretA
        num = random.randint(1, 100)
        len = random.randint(1, 100)
        udp_port = random.randint(4096, 65535)
        secretA = random.randint(1, 100)
        payload = struct.pack('!IIII', num, len, udp_port, secretA)
        packet_send = createHeaderandPackagePayload(payload, 0, STEP1, DIGITS)
        s.sendto(packet_send, client_adddr)

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = socket.gethostbyname(socket.gethostname())
    addressInfo = socket.getaddrinfo(server, PORT)
    s.bind(addressInfo[0][4])
    while True:
        udp_client_data = s.recvfrom(BUFFERSIZE)
        client_data = udp_client_data[0]
        client_adddr = udp_client_data[1]
        thread = threading.Thread(target = p2StageA, args = (s, client_data, client_adddr))
        thread.start()
