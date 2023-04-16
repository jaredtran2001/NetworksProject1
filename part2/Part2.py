#from part1.Part1 import *
import socket
import struct
import threading
import random

BUFFERSIZE = 1024
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
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((SERVER_ADDRESS, PORT))
    while True:
        print("Waiting for client...")
        client_data, client_addr = s.recvfrom(BUFFERSIZE)
        print("Received message from client")
        p2StageA(s, client_data, client_addr)
        # thread = threading.Thread(target = p2StageA, args = (s, client_data, client_addr))
        # thread.start()
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
    print("Responding with UDP packet for Stage A...")
    s.sendto(payload, client_addr)
    p2StageB(s, client_addr, num, len, secretA)

def p2StageB(s, client_addr, num, len, secretA):
    print("Receiving", num, "packets for Stage B...")
    num_recv = 0
    while num_recv < num:
        client_data, client_addr2 = s.recvfrom(BUFFERSIZE)
        header_data = client_data[:HEADERSIZE]
        header_data = struct.unpack('!IIHH', header_data)
        # verify header data
        if header_data != (len + 4, secretA, STEP1, DIGITS):
            print("Incorrect header: ", header_data)
            return
        # get packet_id
        client_payload = struct.unpack('!I', client_data[HEADERSIZE:HEADERSIZE + 4])
        # randomly decide whether to send ack
        if random.random() < 0.5:
            #TODO: NEED TO CHECK PAYLOAD SEND FROM CLIENT, APPEARS TO BE IN TUPLE FORM?
            ack_packet = struct.pack('!IIHHI', 4, secretA, STEP2, DIGITS, client_payload[0])
            num_recv += 1
        else:
            ack_packet = struct.pack('!IIHHI', 4, secretA, STEP2, DIGITS, num + 1)
        s.sendto(ack_packet, client_addr)
        
    print("Received all", num, "packets. Sending packet for steb b2...")
    # step b2
    tcp_port = random.randint(4096, 65535)
    secretB = random.randint(1, 100)
    payload = struct.pack('!IIHHII', 8, secretA, STEP2, DIGITS, tcp_port, secretB)
    s.sendto(payload, client_addr)


if __name__ == '__main__':
    main()
