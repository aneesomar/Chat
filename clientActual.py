import socket
import threading
import atexit

nickname = input("Choose your nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 1358))

# flag to signal threads to stop
stop_threads = False


def send_end_message():
    end_message = '/end'
    client.send(end_message.encode('ascii'))
    client.close()


atexit.register(send_end_message)


def receive():
    global stop_threads
    while True:
        if stop_threads:
            break
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            elif message == '/end':
                print("Received end command from server. Closing connection.")
                stop_threads = True
            elif message.startswith("Connected clients:"):
                print("Requesting list of clients from server.")
                client.send('list'.encode('ascii'))

            else:
                print(message)
        except:
            print("An error occured!")
            client.close()
            break


def write():
    global stop_threads
    recipient = input(
        "Enter the recipient's nickname (or 'all' for everyone): ")
    while True:
        if stop_threads:
            break
        message = input("Enter your message (or '/new' to change recipient): ")
        if message == '/new':
            recipient = input(
                "Enter the new recipient's nickname (or 'all' for everyone): ")
            continue
        formatted_message = '{}->{}: {}'.format(nickname, recipient, message)
        client.send(formatted_message.encode('ascii'))
        if message == '/end':
            stop_threads = True


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
