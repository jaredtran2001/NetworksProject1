from part1.Part1 import *
import socket
import struct
import threading
import random

BUFFERSIZE = 1024

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((SERVER_ADDRESS, PORT))
    while True:
        print("Waiting for client...")
        client_data, client_addr = s.recvfrom(BUFFERSIZE)
        print("Received message from client")
        thread = threading.Thread(target = p2StageA, args = (s, client_data, client_addr))
        thread.start()
    s.close()

def p2StageA(s, client_data, client_addr):
    # receive packet from client
    header_data = client_data[:HEADERSIZE]
    header_data = struct.unpack('!IIHH', header_data)
    # verify header data
    if header_data != (11, 0, STEP1, DIGITS):
        print("Incorrect header: ", header_data)
        return
    # verify payload
    payload_len = header_data[0]
    client_payload = client_data[HEADERSIZE:HEADERSIZE + payload_len]
    if client_payload != b'hello world':
        print("Incorrect message payload from client: ", client_payload)
        return

    # randomly generate num, len, udp_port, and secretA
    num = random.randint(1, 50)
    len = random.randint(1, 50)
    udp_port = random.randint(4096, 65535)
    secretA = random.randint(1, 100)
    payload = struct.pack('!IIHHIIII', SERVERPACKAGESIZE, 0, STEP1, DIGITS, num, len, udp_port, secretA)
    print("Responding with UDP packet for Stage A to...")
    s.sendto(payload, client_addr)

if __name__ == '__main__':
    main()
