from part1.Part1 import *
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
        print("\tWaiting for client...")
        client_data, client_addr = s.recvfrom(BUFFERSIZE)
        print("\tReceived message from client")
        thread = threading.Thread(target = p2_stage_a, args = (client_data, client_addr))
        thread.start()
    s.close()

def p2_stage_a(client_data, client_addr):
    # receive packet from client
    header_data = client_data[:HEADERSIZE]
    header_data = struct.unpack('!IIHH', header_data)
    # verify header data
    if header_data != (12, 0, STEP1, DIGITS):
        print("\tIncorrect header: ", header_data)
        return
    # verify payload
    payload_len = header_data[0]
    client_payload = client_data[HEADERSIZE:HEADERSIZE + payload_len]
    if client_payload != b'hello world\x00':
        print("\tIncorrect message payload from client: ", client_payload)
        return

    # randomly generate num, len, udp_port, and secretA
    num = random.randint(1, 50)
    len = random.randint(1, 50)
    udp_port = random.randint(4096, 65535)
    secretA = random.randint(1, 100)
    payload = struct.pack('!IIHHIIII', SERVERPACKAGESIZE, 0, STEP1, DIGITS, num, len, udp_port, secretA)
    print("\tResponding with UDP packet for Stage A...")
    sock_a = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_a.sendto(payload, client_addr)
    sock_a.close()
    print("\tSTAGE a complete.")
    p2_stage_b(client_addr, udp_port, num, len, secretA)

def p2_stage_b(client_addr, udp_port, num, len, secretA):
    print("\tStarting STAGE b...")
    sock_b = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_b.bind((SERVER_ADDRESS, udp_port))

    print("\tReceiving", num, "packets for Stage B...")
    num_recv = 0
    if (len + 4) % 4 == 0:
        byte_aligned_len = len + 4
    else:
        byte_aligned_len = (4 - (len + 4) % 4) + (len + 4)

    while num_recv < num:
        client_data, client_addr2 = sock_b.recvfrom(BUFFERSIZE)
        header_data = client_data[:HEADERSIZE]
        header_data = struct.unpack('!IIHH', header_data)
        # verify header data
        if header_data != (byte_aligned_len, secretA, STEP1, DIGITS):
            print("\tIncorrect header: ", header_data)
            return
        # get packet_id
        client_payload = struct.unpack('!II', client_data[HEADERSIZE:HEADERSIZE + 8])
        # randomly decide whether to send ack, respond with incorrect packet_id if not ack
        if random.random() < 0.5:
            ack_packet = struct.pack('!IIHHI', 4, secretA, STEP2, DIGITS, client_payload[0])
            num_recv += 1
        else:
            ack_packet = struct.pack('!IIHHI', 4, secretA, STEP2, DIGITS, num + 1)
        sock_b.sendto(ack_packet, client_addr)
        
    print("\tReceived all", num, "packets. Sending packet for steb b2...")
    # step b2
    tcp_port = random.randint(4096, 65535)
    secretB = random.randint(1, 100)
    payload = struct.pack('!IIHHII', 8, secretA, STEP2, DIGITS, tcp_port, secretB)
    sock_b.sendto(payload, client_addr)
    sock_b.close()
    print("\tSTAGE b complete.")
    p2_stage_c(tcp_port, secretB)

def p2_stage_c(tcp_port, secretB):
    print("\tStarting STAGE c...")
    sock_c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_c.bind((SERVER_ADDRESS, tcp_port))
    sock_c.listen()
    client_conn, client_addr = sock_c.accept()
    num2 = random.randint(1, 50)
    len2 = random.randint(1, 50)
    secretC = random.randint(1, 100)
    char_c = 'c'
    tcp_payload = struct.pack('!IIIc', num2, len2, secretC, char_c.encode('UTF-8'))
    tcp_packet = package_header_and_payload(tcp_payload, secretB, STEP2, DIGITS)
    sock_c.sendto(tcp_packet, client_addr)
    print("\tSTAGE c complete.")
    p2_stage_d(client_conn, num2, secretC, len2, client_addr)
    sock_c.close()

def p2_stage_d(client_conn, num2, secretC, len2, client_addr):
    print("\tStarting STAGE d...")
    if len2 % 4 == 0:
        byte_aligned_len = len2
    else:
        byte_aligned_len = (4 - len2 % 4) + len2
    
    num_recv = 0
    while num_recv < num2:
        client_data = client_conn.recv(BUFFERSIZE)
        header_data = client_data[:HEADERSIZE]
        header_data = struct.unpack('!IIHH', header_data)
        # verify header data
        if header_data != (byte_aligned_len, secretC, STEP1, DIGITS):
            print("\tIncorrect header: ", header_data)
            return
        # verify payload data that all are of the character c
        client_payload = client_data[HEADERSIZE:HEADERSIZE + len2]
        if not all(i == 'c' for i in client_payload):
            print("\tIncorrect payload: ", client_payload)
            return
        num_recv += 1

    # step d2
    secretD = random.randint(1, 100)
    d_payload = struct.pack('!IIHHI', 4, secretD, STEP2, DIGITS, secretD)
    client_conn.sendto(d_payload, client_addr)
    print("\tSTAGE d complete.")


if __name__ == '__main__':
    main()
