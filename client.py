import pickle
import os
from re import U
import socket as sk
import string
import time

downloadLocation = os.getcwd()+"/client/download/"
uploadLocation = os.getcwd()+"/client/upload"

def send(msg)->str:
    sent = sock.sendto(msg.encode(), server_address)
    data, server = sock.recvfrom(32768)
    print('%s\n\r' % data.decode('utf8'))
    return data.decode('utf8')

sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

server_address = ('localhost', 10000)

message = '\n\rConnecting to server...'

print(message)

try:
    sent = sock.sendto(message.encode(), server_address)
    #receive message
    data, server = sock.recvfrom(32768)
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
            sent = sock.sendto(message.encode(), server_address)
            data, server = sock.recvfrom(32768)
            if  data.decode('utf8') == 'File not found':
                print('ERROR: File not found\n\r')
            else:
                print('%s\n\r' % data.decode('utf8'))
                #receive message length
                data, server = sock.recvfrom(32768)
                msgLength = int(data.decode('utf8'))
                print('%s\n\r' % data.decode('utf8'))

                listOfPackets=[]
                
                for i in range(msgLength):
                    data, server = sock.recvfrom(32768)
                    data = pickle.loads(data)
                    listOfPackets.append(data)
                    print(f"{data['index']}/{msgLength}", end='\r')

                listOfPackets.sort(key=lambda x: x['index'])
                with open(downloadLocation + message[4:], "wb") as newFile:
                    for i in listOfPackets:
                        newFile.write(i['bytes'])
                print(f"Downloaded {message[4:]} file from server")

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
