import socket as sk
import os
import math
import pickle
import hashlib
from time import sleep
from typing import List
from utils import *

sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

server_address = ('localhost', 10000)
print('\n\rStarting un on %s port %s' % server_address)
sock.bind(server_address)

pathToFiles = os.getcwd()+"/server/storedFiles/"

# Function to send the Help message.
def sendHelpMessage(sock, address):
    """
    It sends a help message to the client
    
    :param sock: the socket object
    :param address: The address of the server
    """
    m1 = 'Hello, please type a command from the followings: \n\r\n\r' 
    m2 = 'List -> view the files in the archive\n\rGet "filemane" -> downloand the file from the archive\n\r' 
    m3 = 'Put "filemane" -> upload the file to the archive\n\rQuit -> exit the program\n\r'
    m4 = 'Help -> show this message again'
    mainMessage = m1 + m2 + m3 + m4
    sock.sendto(mainMessage.encode(), address)

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


def files(path):
    """
    It returns a list of all the files in a directory, excluding hidden files
    
    :param path: the path to the directory you want to list
    :return: A list of files in the directory.
    """
    l = os.listdir(path)
    for f in l:
        if f.startswith("."):
            l.remove(f)
    return l

def fileLength(fileName:str)->int:
    """
    It takes a file name as a string, opens the file, reads the file, and returns the number of packets
    that will be needed to send the file
    
    :param fileName: The name of the file you want to get the length of
    :type fileName: str
    :return: The number of packets that will be sent to the client.
    """
    fileName= pathToFiles+"/"+fileName
    with open(fileName, "rb") as file:
        response = file.read()
    numOfPackets = 1
    size = len(response)
    if size > PACKET_SIZE:
        numOfPackets = math.ceil(size / PACKET_SIZE)
    return numOfPackets

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

try:
    
    while True:
        print('\n\rWaiting to receive a message...\n\r')
        data, address = sock.recvfrom(BUFF) 
        resp = data.decode('utf8')
        if data:
            sendHelpMessage(sock, address)
            print('User has connected\n\r')
            print('Sent help message\n\r')
            while True:
                action, address = sock.recvfrom(BUFF)
                response = action.decode('utf8')

                # Download the file
                if response[0:3].lower() == 'get':
                    # Get the file name
                    fileName = response[4:]
                    try:
                        # Get the number of packets
                        numOfPackets = fileLength(fileName)
                    except IOError:
                        print('File not found\n\r')
                        sock.sendto('404'.encode(), address)
                        continue
                    print('Sending the file to the client...\n\r')
                    # Send ACK
                    sock.sendto("ACK".encode(), address)
                    # Send the number of packets
                    sock.sendto(str(numOfPackets).encode(), address)
                    # Send the list of packets
                    List = getList(pathToFiles, fileName, numOfPackets)
                    print(f"Sending packages...")
                    # Send the packets
                    for i in List:
                        sock.sendto(pickle.dumps(i), address)
                        sleep(SLEEP)
                    # Send the hash of the file
                    sock.sendto(hashList(List).encode(), address)
                    print('File sent!!\n\r')

                # Upload the file
                elif response[0:3].lower() == 'put':
                    print('Storing the file the client has sent...\n\r')
                    # Get the file name
                    fileName = response[4:]
                    # Send ACK
                    sock.sendto("ACK".encode(), address)
                    # Receive number of packets
                    response, client = sock.recvfrom(BUFF)
                    msgLength = int(response.decode('utf8'))
                    # Create list of packets
                    listOfPackets=[]
                    # Fills the list of packets with the packets data
                    for i in range(msgLength):
                        response, client = sock.recvfrom(BUFF)
                        response = pickle.loads(response)
                        listOfPackets.append(response)
                        print(f"{response['pos']}/{msgLength}", end='\r')
                    # Sort the list of packets by position
                    listOfPackets.sort(key=lambda x: x['pos'])
                    data, server = sock.recvfrom(BUFF)
                    hash = data.decode('utf8')
                    if hash != hashList(listOfPackets):
                        print('ERROR: File corrupted\n\r')
                    else:
                        with open(pathToFiles + fileName, "wb") as newFile:
                            for i in listOfPackets:
                                newFile.write(i['value'])
                        print(f"Stored {fileName} file from Client")
                    

                # Send help message
                elif response.lower() == 'help':
                    print('Sending help message...\n\r')
                    sendHelpMessage(sock, address)

                # Show file in folder
                elif response.lower() == 'list':
                    print('Showing files...\n\r')
                    data = 'Files stored are: ' + str(files(pathToFiles))
                    sock.sendto(data.encode(), address)

                # Quit the program
                elif response.lower() == 'quit':
                    print('Closing the program')
                    sock.close()
                    break
                
                # Invalid command or another user has connected
                else:
                    sendHelpMessage(sock, address)
        break
except Exception as error:
    print(error)

