import socket
import os
import time

# Get the amount of packets required to send the file if we
# want each packet to hold a maximum of buffer_size


def get_file_packet_count(filename, buffer_size):
    byte_size = os.stat(filename).st_size

    packet_count = byte_size//buffer_size

    if byte_size % buffer_size:
        packet_count += 1

    return packet_count

# Send a message and wait for confirmation response


def send_packet(sock, data, target, buff_size):
    sock.sendto(data, target)

    while True:
        try:
            data, messenger = sock.recvfrom(buff_size)
            data = data.decode()

            if data == "CONFRIMED":
                break
        except:
            continue

    time.sleep(0.00001)


def send_file(IP, port, filename):
    message = "%s***%s***%d"

    # Setup our socket and constants
    MY_PORT = 4498
    MY_ADDR = "127.0.0.1"
    buff_size = 1024 * 5

    target = (IP, port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((MY_ADDR, MY_PORT))
    sock.settimeout(.02)
    data = None

    # Ping client until it is no longer busy
    while not data == "READY":
        ready_message = message % ("IS_READY", "_", 0)
        sock.sendto(ready_message.encode(), target)
        time.sleep(0.001)

        try:
            data, messenger = sock.recvfrom(buff_size)
            data = data.decode()
        except:
            pass

        time.sleep(0.01)

    packet_count = get_file_packet_count(filename, buff_size)

    # Initial file transfer
    init_message = message % (
        "INITIATE", "Duplicate_" + filename, packet_count)
    sock.sendto(init_message.encode(), target)

    f = open(filename, "rb")

    if sock is not None:
        print("Sending %s with %d packets" % (filename, packet_count))
        for i in range(0, packet_count):
            send_packet(sock, f.read(buff_size), target, buff_size)

    print("Sent all %d packets\n" % (packet_count))
    f.close()
