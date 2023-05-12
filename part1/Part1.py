import socket
import struct
import sys

SERVER_ADDRESS = None
PORT = 12235
STEP1 = 1
DIGITS = 887
HEADER_SIZE = 12
SERVER_ACK_SIZE_STAGE_A = 16
SERVER_ACK_SIZE_STAGE_B = 4
SERVER_ACK_SIZE_STAGE_C = 13
SERVER_ACK_SIZE_STAGE_D = 4


def main():
    if(len(sys.argv) != 2):
        print("Need to provide a Server Address")
        sys.exit()
    else :
        global SERVER_ADDRESS
        SERVER_ADDRESS = sys.argv[1]
    stage_a_res, secret_a = p1_stage_a()
    stage_b_res, secret_b, tcp_port = p1_stage_b(stage_a_res)
    stage_c_res, secret_c, socket_tcp, tcp_port = p1_stage_c(
        stage_b_res, tcp_port)
    secret_d = p1_stage_d(stage_c_res, socket_tcp, tcp_port)
    secrets = []
    secrets.append(secret_a)
    secrets.append(secret_b)
    secrets.append(secret_c)
    secrets.append(secret_d)
    print(f"Part 1 Extracted Secrets: {secrets}")
    sys.exit()


def p1_stage_a() -> (tuple, int):
    print("\nStarting Stage a...\n")
    # create udp socket
    sock = create_udp_socket()
    payload = b'hello world\0'

    # package and send packet to the server
    send_data = package_header_and_payload(payload, 0, STEP1, DIGITS)
    print(f"\tSending UDP packet to {SERVER_ADDRESS} on port {PORT}...")
    sock.sendto(send_data, (SERVER_ADDRESS, PORT))

    # receive packet from the server
    print(f"\tReceiving UDP packet from {SERVER_ADDRESS}... ")
    recv_data, server_address = sock.recvfrom(
        HEADER_SIZE + SERVER_ACK_SIZE_STAGE_A)
    recv_buf = struct.unpack("!IIII", recv_data[HEADER_SIZE:])
    print("\n\n\tPacket contents: ", recv_buf[:])
    num = recv_buf[0]
    length = recv_buf[1]
    udp_port = recv_buf[2]
    secret_a = recv_buf[3]
    print(f"\t\tnum: {num} \
          \n\t\tlen: {length} \
          \n\t\tudp_port: {udp_port} \
          \n\t\tsecretA: {secret_a}")
    sock.close()
    print("STAGE a complete.\n\n")
    return recv_buf, secret_a


def p1_stage_b(recv_buf) -> (tuple, int, int):
    print("\nStarting Stage b...\n")
    sock = create_udp_socket()
    sock.settimeout(0.5)
    num = recv_buf[0]
    len = recv_buf[1]
    udp_port = recv_buf[2]
    secret = recv_buf[3]
    i = 0
    while i < num:
        # create the payload
        payload = bytearray(len + 4)
        int_bytes = struct.pack('!I', i)
        payload[0:4] = int_bytes[0:4]

        # add the header to the payload
        send_data = package_header_and_payload(
            payload, secret, STEP1, DIGITS)

        # send data to server
        print(f"\tSending UDP packet to  "
              + f" {SERVER_ADDRESS} on port {udp_port}...")
        sock.sendto(send_data, (SERVER_ADDRESS, udp_port))

        try:
            # receive data from server
            print(f"\tReceiving packet {i} from {SERVER_ADDRESS}...")
            recv_data, server_address = sock.recvfrom(
                HEADER_SIZE + SERVER_ACK_SIZE_STAGE_B)
            recv_buf = struct.unpack("!I", recv_data[HEADER_SIZE:])
            if recv_buf[0] == i:
                i += 1
        except socket.timeout:
            print(f"\t\tRetrying...")
            continue

    recv_data, recAddr = sock.recvfrom(HEADER_SIZE + 8)
    recv_buf = struct.unpack("!II", recv_data[HEADER_SIZE:])
    print(f"\n\n\tPacket contents: {recv_buf[:]}")
    tcp_port = recv_buf[0]
    secret_b = recv_buf[1]
    print(f"\t\ttcp_port: {tcp_port} \
          \n\t\tsecretB: {secret_b}")
    print("STAGE b complete.\n\n")
    sock.close()
    return recv_buf, secret_b, tcp_port


def p1_stage_c(recv_buf, tcp_port) -> (tuple, int, socket.socket, int):
    print("Starting STAGE c...\n")
    sock = create_tcp_socket(SERVER_ADDRESS, tcp_port)

    # receive data from the server
    print(f"\tReceving TCP packet from"
          + f" {SERVER_ADDRESS} on port {tcp_port}...")
    recv_data = sock.recv(HEADER_SIZE + SERVER_ACK_SIZE_STAGE_C)
    recv_buf = struct.unpack("!IIIc", recv_data[HEADER_SIZE:])
    print(f"\n\n\tPacket contents: {recv_buf[:]}")
    num2 = recv_buf[0]
    len2 = recv_buf[1]
    secret_c = recv_buf[2]
    c = recv_buf[3]
    print(f"\t\tnum2: {num2} \
          \n\t\tlen2: {len2} \
          \n\t\tsecretC: {secret_c} \
          \n\t\tc: {c}")
    print("STAGE c complete.\n\n")
    return recv_buf, secret_c, sock, tcp_port


def p1_stage_d(recv_buf, sock, tcp_port) -> int:
    print("Starting STAGE d...\n")
    num2 = recv_buf[0]
    len2 = recv_buf[1]
    secret_c = recv_buf[2]
    c = recv_buf[3]
    sock.settimeout(3)
    i = 0
    while i < num2:
        payload = c.decode() * len2
        payload = payload.encode()
        char_bytes = struct.pack('!%ds' % len2, payload)

        # add the header to the payload
        send_data = package_header_and_payload(
            char_bytes, secret_c, STEP1, DIGITS)    
        # send data to server
        if i == 0:
            print(f"\tPacket being sent to server {num2} times: {send_data}\n")
        print(
            f"\tSending TCP packet to {SERVER_ADDRESS} on port {tcp_port}...")
        sock.sendto(send_data, (SERVER_ADDRESS, tcp_port))
        i += 1

    # server seems to respond first with 3 bytes of character c
    # then with header + payload containing secretD
    # iff it received num2 correct payloads first
    for i in range(2):
        try:
            print(f"\tReceving TCP packet from"
                  + f" {SERVER_ADDRESS} on port {tcp_port}...")
            recv_data = sock.recv(HEADER_SIZE + SERVER_ACK_SIZE_STAGE_D)
            print(f"\tPacket contents: {recv_data}")
            if recv_data == b'' or len(recv_data) > 3:
                break
        except socket.timeout:
            print(f"\tRetrying... \n")
            continue
    recv_buf = struct.unpack("!I", recv_data[HEADER_SIZE:])
    secret_d = recv_buf[0]
    print(f"\tPacket contents: {recv_buf[:]}")
    secred_d = recv_buf[0]
    print(f"\t\tsecretD: {secred_d}")
    print("STAGE d complete.\n\n")
    sock.close()
    return secret_d


def create_tcp_socket(addr, port) -> socket.socket:
    """Creates TCP socket and gets addr info."""
    dns_resolved_addr = socket.gethostbyname(SERVER_ADDRESS)
    socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_tcp.connect((addr, port))
    return socket_tcp


def create_udp_socket() -> socket.socket:
    """"Creates UDP socket and gets addr info."""
    dns_resolved_addr = socket.gethostbyname(SERVER_ADDRESS)
    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # socket_udp.connect((dns_resolved_addr, PORT))
    return socket_udp


def package_header_and_payload(payload, secret, step, digits) -> bytes:
    """Creates the 12-byte header and padded payload packet."""
    payload_len = len(payload)
    header = struct.pack("!IIHH", payload_len, secret, step, digits)
    return header + payload.ljust(pad_length(payload), b'\0')


def pad_length(payload) -> int:
    """Computes padding needed for payload to be 4-byte aligned."""
    if len(payload) % 4 == 0:
        payload_len = len(payload)
    else:
        payload_len = (4 - len(payload) % 4) + len(payload)
    return payload_len


if __name__ == '__main__':
    main()
