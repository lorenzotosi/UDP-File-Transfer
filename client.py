import os
import socket as sk
import string
import time

downloadLocation = os.getcwd()+"/client/download"
uploadLocation = os.getcwd()+"/client/upload"

def send(msg):
    sent = sock.sendto(msg.encode(), server_address)
    data, server = sock.recvfrom(4096)
    print('%s\n\r' % data.decode('utf8'))

sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

server_address = ('localhost', 10000)

message = '\n\rConnecting to server...'

print(message)

try:
    sent = sock.sendto(message.encode(), server_address)
    #receive message
    data, server = sock.recvfrom(4096)
    print('%s\n\r' % data.decode('utf8'))


    while True:
        print('Write a command:')
        message = input()

        if message.lower() == 'quit':
                print('Closing the program')
                sent = sock.sendto(message.encode(), server_address)
                sock.close()
                break

        elif message[0:3].lower() == 'get':
            print('\n\rDownloading file...')
            send(message.lower())

        elif message[0:3].lower() == 'put':
            print('\n\rUploading file...')
            send(message.lower())

        elif message.lower() == 'list':
            print('\n\rShowing files...')
            send(message.lower())

        elif message.lower() == 'help':
            print('\n\rShowing help...')
            send(message.lower())

        else:
            print('\n\rInvalid command')
            send(message.lower())
except Exception as info:
        print(info)
