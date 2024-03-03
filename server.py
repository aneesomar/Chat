import socket
import threading
import os

host = '127.0.0.1'
port_TCP = 1395
port_UDP = port_TCP + 1

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port_TCP))
server.listen()

# -------------------------------------------------------------------------------

# UDP socket for file transfer

buffer = 1024 * 5
message = "%s***%s***%d"


server_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_UDP.bind((host, port_UDP))


# packet count

def get_packet_size(file, buffer):
    bytes = os.stat(file).st_size
    packets = bytes//buffer

    if bytes % buffer != 0:
        packets += 1

    return packets


def send_packet(data):
    server_UDP.sendto(data, (host, port_UDP))

    while True:
        try:
            data, messenger = server_UDP.recvfrom(buffer)
            data = data.decode()
            if data == "CONFIRMED":
                break
        except:
            continue


def send_file(file):
    data = None

    while not data == "READY":
        ready_message = message % ("IS_READY", "_", 0)
        server_UDP.sendto(ready_message.encode(), (host, port_UDP))

        try:
            data, messenger = server_UDP.recvfrom(buffer)
            data = data.decode()
        except:
            pass

    packet_count = get_packet_size(file, buffer)

    init_message = message % (
        "INITIATE", "Duplicate_" + file, packet_count)
    server_UDP.sendto(init_message.encode(), (host, port_UDP))

    f = open(file, "rb")

    if server_UDP is not None:
        print("Sending %s with %d packets" % (file, packet_count))
        for i in range(0, packet_count):
            send_packet(f.read(buffer))

    print("Sent all %d packets\n" % (packet_count))
    f.close()
# ------------------------------------------------------------------------------


print("Server Started...")

clients = []
nicknames = []
unhiddenClientsNick = []
addresses = []


def broadcast(message):
    for client in clients:
        client.send(message)


def list_clients():
    if nicknames:
        return "Connected clients: " + ", ".join(nicknames)
    else:
        return "No clients connected."


def listOnlineClients():
    if unhiddenClientsNick:
        return "Connected clients: " + ", ".join(unhiddenClientsNick)
    else:
        return "No clients connected."


def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('ascii')

            if message == '/end':
                client.send("Connection closed.".encode('ascii'))
                index = clients.index(client)
                clients.remove(client)
                nick = nicknames[index]
                if nick in unhiddenClientsNick:
                    unhiddenClientsNick.remove(nick)
                    broadcast("{} left the server.".format(
                        nick).encode('ascii'))
                nicknames.remove(nick)
                client.close()
                break

            elif message == '/list':
                client.send(listOnlineClients().encode('ascii'))

            elif message.startswith("/whisper"):
                parts = message.split(maxsplit=3)

                sender = parts[1]
                recip = parts[2]
                msgToSend = parts[3]

                privateMessage(sender, recip, msgToSend)

            elif message.startswith('/hide'):
                nickToHide = message.split()[1]
                for client, nickname in zip(clients, nicknames):
                    if nickname == nickToHide and nickname in unhiddenClientsNick:
                        unhiddenClientsNick.remove(nickname)
                        client.send(
                            "Your connection is hidden from other users.".encode('ascii'))
                        broadcast("{} left the server.".format(
                            nickname).encode('ascii'))
                    elif nickname == nickToHide and nickname not in unhiddenClientsNick:
                        client.send(
                            "Your connection is already hidden from other users.".encode('ascii'))

            elif message.startswith('/unhide'):
                nickToUnhide = message.split()[1]
                for client, nickname in zip(clients, nicknames):
                    if nickname == nickToUnhide and nickname in unhiddenClientsNick:
                        client.send(
                            "Your connection is already available to other users.".encode('ascii'))
                    elif nickname == nickToUnhide and nickname not in unhiddenClientsNick:
                        client.send(
                            "Your connection is now available to other users.".encode('ascii'))
                        unhiddenClientsNick.append(nickname)
                        broadcast("{} joined the server.".format(
                            nickname).encode('ascii'))

            elif message.startswith('/addr'):
                parts = message.split(maxsplit=3)

                clientNickname = parts[1]
                # client.send(listOnlineClients().encode('ascii'))

                # find client by nickname
                for address, nickname in zip(addresses, nicknames):
                    if nickname == clientNickname:
                        # convert address to string
                        str = "{}:{}".format(address[0], address[1])
                        client.send(str.encode('ascii'))
                        # print(str)
                        break

            elif message == '/file':
                input_file = input("Enter file name: ")
                recipient = input("Enter recipient: ")
                recipClient = findRecipient(recipient)
                if recipClient:
                    send_file(input_file)
                else:
                    print("Unable to find recipient")

            else:
                broadcast(message.encode('ascii'))
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast('{} left the server.'.format(nickname).encode('ascii'))
            nicknames.remove(nickname)
            break


def privateMessage(sender, recipient, message):
    recipClient = findRecipient(recipient)
    if recipClient:
        formattedMsg = "{} -> {}: {}".format(sender, recipient, message)
        recipClient.send(formattedMsg.encode('ascii'))
    else:
        sender.send("Unable to find recipient :/".encode('ascii'))


def findRecipient(recipNick):  # find recipient to priv msg
    for client, nickname in zip(clients, nicknames):
        if nickname == recipNick:
            return client
    return None


def findAddress(clientNickname):
    for address, nickname in zip(addresses, nicknames):
        if nickname == clientNickname:
            return address
    return None


def receive():
    while True:
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        nickname = client.recv(1024).decode('ascii').strip()

        while ' ' in nickname or nickname in nicknames:
            if ' ' in nickname:
                client.send("NICK_CONTAIN_WHITESPACE".encode('ascii'))
            else:
                client.send("NICK_NOT_UNIQUE".encode('ascii'))
            nickname = client.recv(1024).decode('ascii').strip()

        client.send("NICK_ACCEPTED".encode('ascii'))

        nicknames.append(nickname)
        clients.append(client)
        addresses.append(address)
        unhiddenClientsNick.append(nickname)

        print("Nickname is {}".format(nickname))
        broadcast("{} joined the server.".format(nickname).encode('ascii'))
        client.send(
            'Connected to server!\nType /help for list of commands'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


receive()
