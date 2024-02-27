import socket
import threading

nickname = input("Choose a nickname: ")


# create socket object with ipv4 and tcp protocol
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# instead of binding to a server we connect
client.connect(('127.0.0.1', 55555))


def receive():
    while True:
        try:
            # recieve message from server
            message = client.recv(1024).decode('ascii')
            # if message = "nick" send nickname otheriwse we print the msg
            if message == 'NICK':
                # send nickname to server
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            # if doesnt work just close connection
            print("An error occured!")
            client.close()
            break


def write():
    while True:
        message = f'{nickname}: {input("")}'  # input message and add nickname
        client.send(message.encode('ascii'))


receive_thread = threading.Thread(target=receive)  # create thread for recieve
receive_thread.start()  # start thread

write_thread = threading.Thread(target=write)  # create thread for write
write_thread.start()  # start thread
