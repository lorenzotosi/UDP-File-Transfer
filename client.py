import math
import pickle
import os
import socket as sk
import hashlib
from time import sleep
from utils import *
from typing import List

downloadLocation = os.getcwd()+"/client/download/"
uploadLocation = os.getcwd()+"/client/upload/"

def hashList(List:List)->str:
    """
    It takes a list of dictionaries, and returns a string that is the hash of the list of dictionaries
    
    :param List: The list of dictionaries you want to hash
    :type List: List
    :return: A string that is the hash of the list of dictionaries
    """
    hash = hashlib.sha256()
    for i in List:
        hash.update(pickle.dumps(i))
    return hash.hexdigest()

def send(msg)->str:
    sent = sock.sendto(msg.encode(), server_address)
    data, server = sock.recvfrom(BUFF)
    print('%s\n\r' % data.decode('utf8'))
    return data.decode('utf8')

def getList(pathToFiles, fileName, numOfPackets) -> List:
    """
    It takes a path to a file, the name of the file, and the number of packets to be sent, and returns a
    list of dictionaries, each dictionary containing the index of the packet and the value of the packet
    
    :param pathToFiles: The path to the folder where the files are stored
    :param fileName: The name of the file you want to send
    :param numOfPackets: The number of packets that the file will be split into
    :return: A list of dictionaries. Each dictionary has two keys: position and value.
    """
    with open(pathToFiles + fileName, "rb") as file:
        List = []
        for i in range(numOfPackets):
            toSend = {"pos": i, "value": file.read(PACKET_SIZE)}
            List.append(toSend)
    return List

def fileLength(fileName:str)->int:
    """
    It takes a file name as a string, opens the file, reads the file, and returns the number of packets
    that will be needed to send the file
    
    :param fileName: The name of the file you want to get the length of
    :type fileName: str
    :return: The number of packets that will be sent to the client.
    """
    fileName= uploadLocation+"/"+fileName
    with open(fileName, "rb") as file:
        response = file.read()
    numOfPackets = 1
    size = len(response)
    if size > PACKET_SIZE:
        numOfPackets = math.ceil(size / PACKET_SIZE)
    return numOfPackets

sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

server_address = ('localhost', 10000)

message = '\n\rConnecting to server...'

print(message)

try:
    sent = sock.sendto(message.encode(), server_address)
    #receive message
    data, server = sock.recvfrom(BUFF)
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
            data, server = sock.recvfrom(BUFF)
            if  data.decode('utf8') == 'no':
                print('ERROR: File not found\n\r')
            else:
                print('%s\n\r' % data.decode('utf8'))
                # Receive message length
                data, server = sock.recvfrom(BUFF)
                msgLength = int(data.decode('utf8'))
                # Create list of packets
                listOfPackets=[]
                # Fills the lisf of packets with the packets data
                for i in range(msgLength):
                    data, server = sock.recvfrom(BUFF)
                    data = pickle.loads(data)
                    listOfPackets.append(data)
                    print(f"{data['pos']}/{msgLength}", end='\r')
                # Sort the list of packets by position
                listOfPackets.sort(key=lambda x: x['pos'])
                # Receive the hash of the list of packets from the server
                data, server = sock.recvfrom(BUFF)
                hash = data.decode('utf8')
                if hash != hashList(listOfPackets):
                    print('ERROR: File corrupted\n\r')
                else:
                    with open(downloadLocation + message[4:], "wb") as newFile:
                        for i in listOfPackets:
                            newFile.write(i['value'])
                    print(f"Downloaded {message[4:]} file from server")

        elif message[0:3].lower() == 'put':
            fileName = message[4:]
            try:
                # Get the number of packets
                numOfPackets = fileLength(fileName)
            except IOError:
                    print('File not found\n\r')
                    #sock.sendto('no'.encode(), server_address)
                    continue
            print('\n\rUploading file...')
            # Sends the file name to the server
            sent = sock.sendto(message.encode(), server_address)
            # Send ACK
            sock.sendto("ACK".encode(), server_address)
            # Send the number of packets
            numOfPackets = fileLength(fileName)
            sock.sendto(str(numOfPackets).encode(), server_address)
            # Send the list of packets
            List = getList(uploadLocation, fileName, numOfPackets)
            print(f"Sending packages...")
            # Send the packets
            for i in List:
                sock.sendto(pickle.dumps(i), server_address)
                sleep(SLEEP)
             # Send the hash of the file
            sock.sendto(hashList(List).encode(), server_address)
            print('File sent!!\n\r')

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
