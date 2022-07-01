import os
import socket as sk
import string
import time

downloadLocation = os.getcwd()+"/client/download"
uploadLocation = os.getcwd()+"/client/upload"

def send(msg):
    #print('\n\r%s' % msg)
    sent = sock.sendto(msg.encode(), server_address)
    data, server = sock.recvfrom(4096)
    print('%s\n\r' % data.decode('utf8'))

# a function that ask the server to download a file and download it
def get(fileName):
    msg = 'get ' + fileName
    send(msg)
    data, server = sock.recvfrom(4096)
    print('%s\n\r' % data.decode('utf8'))
    if data.decode('utf8') == 'File not found':
        print('File not found')
    else:
        print('File found')
        send('ok')
        data, server = sock.recvfrom(4096)
        print('%s\n\r' % data.decode('utf8'))
        file = open(downloadLocation+"/"+fileName, "wb")
        file.write(data)
        file.close()
        print('File downloaded')
        send('ok')
    return

sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

server_address = ('localhost', 10000)

message = '\n\rConnecting to server...'

print(message)

sent = sock.sendto(message.encode(), server_address)
data, server = sock.recvfrom(4096)
print('%s\n\r' % data.decode('utf8'))
data, server = sock.recvfrom(4096)
print('%s\n\r' % data.decode('utf8'))

while True:
    try:
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
