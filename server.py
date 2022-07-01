import socket as sk
import os

sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

server_address = ('localhost', 10000)
print('\n\rStarting un on %s port %s' % server_address)
sock.bind(server_address)

pathToFiles = os.getcwd()+"/server/storedFiles"

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

def files(path):
    l = os.listdir(path)
    for f in l:
        if f.startswith("."):
            l.remove(f)
    return l



try:

    while True:

        print('\n\rWaiting to receive a message...\n\r')
        data, address = sock.recvfrom(4096) 
        resp = data.decode('utf8')
        if data:
            #sock.sendto('Connected to server'.encode(), address)
            sendHelpMessage(sock, address)
            
            print('User has connected\n\r')
            print('Sent help message\n\r')
            while True:
                action, address = sock.recvfrom(1024)
                response = action.decode('utf8')

                # Download the file
                if response[0:3].lower() == 'get':
                    print('Sending the file...\n\r')
                    data = "arrivato download, te lo mando indietro" 
                    sent = sock.sendto(data.encode(), address)

                # Upload the file
                elif response[0:3].lower() == 'put':
                    print('Storing the file...\n\r')
                    data = "arrivato upload, te lo mando indietro"
                    sent = sock.sendto(data.encode(), address)

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