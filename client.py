import socket
import threading
from sys import argv, exit
from sendFile import send_file


def get_args(recurred=False):
    try:
        if len(argv) == 3 and not recurred:
            ipAddress = argv[1]
            portNum = int(argv[2])
        elif len(argv) > 1 and not recurred:
            raise ValueError
        else:
            ipAddress = input("Enter server IP address:\n")
            print(ipAddress)
            portNum = int(input("Enter the port number:\n"))
            print(portNum)
        return (ipAddress, portNum)
    except ValueError:
        if len(argv) > 1 and not recurred:
            print("Invalid command line arguments.")
        print("Please enter a valid IP address and port number below.")
        return get_args(recurred=True)


ipAddress, portNum = get_args()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((ipAddress, portNum))
except ConnectionRefusedError:
    print("Connection refused. Make sure the server is running and that the port number is correct.")

nickname = input("Choose your nickname: ")

# flag to signal threads to stop
stop_threads = False

# ------------------------------------------------------------------------------------------------

buffer = 1024 * 5
# server_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# server_UDP.bind((ipAddress, portNum-1))

inStartMode = True  # flag to signal the server to start receiving a file
packets = []  # list to store all the received packets
write_file = None  # file to write the received data to
packetcnt = 0  # number of packets to expect

# if server_UDP is not None:
#     while True:
#         try:
#             data, messenger = server_UDP.recvfrom(buffer)
#         except:
#             continue

#         if inStartMode:
#             data = data.decode()

#             message, filename, packet_count = data.split("***")
#             packet_count = int(packet_count)

#             if message == "INITIATE":
#                 print("Receiving %s with %d packets" %
#                       (filename, packet_count))
#                 write_file = open(filename, "wb")
#                 inStartMode = False
#                 packets = []

#             elif message == "IS_READY":
#                 server_UDP.sendto("READY".encode(), messenger)

#         else:
#             packets.append(data)
#             server_UDP.sendto("CONFIRMED".encode(), messenger)

#             if len(packets) == packet_count:
#                 print("Writing %s with %d packets\n" %
#                       (filename, packet_count))

#                 for packet in packets:
#                     write_file.write(packet)

#                 write_file.close()

#                 inStartMode = True
#                 write_file = None
#                 packet_count = 0
#                 written_packets_count = 0

# ------------------------------------------------------------------------------------------------


def receive():
    global stop_threads
    while not stop_threads:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            print("An error occured!")
            client.close()
            break


def sendFileThread(IP, port, fileName):
    print("Sending file to IP:", IP, "on port:", port)
    print("File name:", fileName)
    send_file("127.0.0.1", 4489, "test.zip")

    # send_file(IP, port, fileName)


def write():
    global stop_threads
    while True:
        if not stop_threads:
            clientInput = input("/all to broadcast, \n/whisper [nickname] for private, \n" +
                                "/list to view online clients, \n/hide to hide presence, \n/unhide to unhide connection, \n" +
                                "/end to leave server: \n")

            if stop_threads:
                break

            partsOfInput = clientInput.strip().split(maxsplit=1)
            command = partsOfInput[0]
            if len(partsOfInput) > 1:
                args = partsOfInput[1].strip().split(sep=' ')
            else:
                args = []
            print("Command:", command, "Args:", args)

            commands = {
                "/all": broadcastToAll,  # broadcast message
                "/list": listOnlineClients,  # request list of online clients,
                "/whisper": privateMessage,  # private message
                "/hide": hideConnection,  # hide presence,
                "/unhide": unhideConnection,
                "/end": exitServer,  # leave server
                "/getAddress": getAddress,  # get address of recipient
                "/sendFile": sendFile
            }

            if command in commands:
                commands[command](*args)
            else:
                print("invalid input!")


def broadcastToAll(message):
    formattdMessage = '{}: {}'.format(nickname, message)
    client.send(formattdMessage.encode('ascii'))


def listOnlineClients():
    client.send("/list".encode('ascii'))


def privateMessage(recip):
    while recip == '' or recip == " ":
        recip = input("Enter nickname of recipient: ")
    message = input("Type a message: ")
    formattedMessage = '/whisper {} {} {}'.format(nickname, recip, message)
    client.send(formattedMessage.encode('ascii'))


def hideConnection():
    client.send("/hide".encode('ascii'))


def unhideConnection():
    client.send("/unhide".encode('ascii'))


def exitServer():
    global stop_threads
    client.send("/end".encode('ascii'))
    stop_threads = True
    client.close()
    print("Connection closed.")


def getAddress(nickname):
    formattedMessage = '/getAddress {}'.format(nickname)
    client.send(formattedMessage.encode('ascii'))


def sendFile(IP, port, fileName):
    # print("Sending file to IP:", IP, "on port:", port)
    receive_thread = threading.Thread(
        target=sendFileThread, daemon=True, args=(IP, port, fileName))
    receive_thread.start()


def main():
    receive_thread = threading.Thread(target=receive, daemon=True)
    receive_thread.start()

    # print("Receive thread started")

    write_thread = threading.Thread(target=write, daemon=True)
    write_thread.start()

    while not stop_threads:
        pass

    exit(0)

    # print("Write thread started")


if __name__ == "__main__":
    main()
