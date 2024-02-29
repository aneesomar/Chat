import socket
from time import time

# Setup our socket and constants
PORT = 4489
MY_ADDR = "127.0.0.1"
buff_size = 1024 * 5

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((MY_ADDR, PORT))
sock.settimeout(.02)

# Initiate some important variables
INIT_MODE = True         # Used to describe whether or not the program is receiving a file
packets = []             # Used to store all of the received packets
f_write_stream = None    # Used to write all of our data to the desired file
packet_count = 0         # Used to tell the script how many packets to expect

if sock is not None:
    while True:
        try:
            data, messenger = sock.recvfrom(buff_size)
        except:
            # Generally timeout errors occur here, not really a worry
            continue

        if INIT_MODE:
            data = data.decode()

            # All messages sent by the server will be in the following format
            # Intent***filename***packet_count
            message, filename, packet_count = data.split("***")

            packet_count = int(packet_count)

            if message == "INITIATE":
                print("Receiving %s with %d packets" %
                      (filename, packet_count))

                f_write_stream = open(filename, "wb")

                INIT_MODE = False
                packets = []

            elif message == "IS_READY":
                sock.sendto("READY".encode(), messenger)

        else:
            packets.append(data)
            sock.sendto("CONFRIMED".encode(), messenger)

            if len(packets) == packet_count:
                print("Writing %s with %d packets\n" %
                      (filename, packet_count))

                for packet in packets:
                    f_write_stream.write(packet)

                f_write_stream.close()

                INIT_MODE = True
                f_write_stream = None
                packet_count = 0
                written_packets_count = 0
