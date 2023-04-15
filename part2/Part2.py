from part1.Part1 import *
import socket
import struct
import threading
import random

BUFFERSIZE = 1024

def p2StageA(conn, addr):
    while True:
        # receive packet from client
        header_data = conn.recv(HEADERSIZE)
        header_data = struct.unpack('!IIHH', header_data)
        # verify header data and if invalid, close client connection
        if header_data != [11, 0, STEP1, DIGITS]:
            print("Incorrect header")
            conn.close()
        payload_len = header_data[0]
        client_payload = conn.recv(payload_len)
        if client_payload != b'hello world':
            print("Incorrect message payload from client")
            conn.close()

        # randomly generate num, len, udp_port, and secretA
        num = random.randint(1, 100)
        len = random.randint(1, 100)
        udp_port = random.randint(4096, 65535)
        secretA = random.randint(1, 100)
        payload = struct.pack('!IIII', num, len, udp_port, secretA)
        packet_send = createHeaderandPackagePayload(payload, 0, STEP1, DIGITS)
        conn.send(packet_send)
        

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addressInfo = socket.getaddrinfo(SERVER_ADDRESS, PORT)
    s.bind(addressInfo[0][4])
    s.listen()
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target = p2StageA, args = (conn, addr))
        thread.start()
