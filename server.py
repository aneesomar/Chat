import socket
import threading


# local host
host = '127.0.0.1'
# random port number
port = 55555

# create socket object with ipv4 and tcp protocol
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
# listen for incoming connections
server.listen()

clients = []
nicknames = []

# broadcast message to all clients


def broadcast(message):
    for client in clients:
        client.send(message)

# handle client connections


def handle(client):
    while True:
        try:
            # try and recieve a msg and then broadcast message to all clients
            message = client.recv(1024)
            broadcast(message)
        except:
            # if doesnt work remove client from list and terminate connection
            index = clients.index(client)  # fetch index of client
            clients.remove(client)
            client.close()  # close connection
            nickname = nicknames[index]  # fetch nickname of client
            nicknames.remove(nickname)
            broadcast(f'{nickname} left the chat!'.encode('ascii'))
            break

# recieve connections from clients


def receive():
    while True:
        # accept incoming connections and store client and address
        client, address = server.accept()
        # print address of client on server console
        print(f"Connected with {str(address)}")

        # send NICK to client to get nickname
        client.send('NICK'.encode('ascii'))
        # recieve nickname from client and decode it to ascii
        nickname = client.recv(1024).decode('ascii')
        # add to lists
        nicknames.append(nickname)
        clients.append(client)

        # print nickname of client on server console
        print(f"Nickname of the client is {nickname}!")
        # broadcast message to all clients that a new client has joined the chat
        broadcast(f"{nickname} joined the chat!".encode('ascii'))
        # send message to client that they are connected to the server
        client.send('Connected to the server!'.encode('ascii'))

        # create a new thread for each client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()  # lol PCP go brrr


print("Server is listening...")
receive()
