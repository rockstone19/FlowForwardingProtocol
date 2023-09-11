#Author: Peter Gutstein
from generalFunctions import *

#Important variables
bufferSize = 65507
time.sleep(1)
#Create the server's socket, declare to controller, and bind it to IP & port
serverID = sys.argv[1]
contAddress = sys.argv[2]
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((sys.argv[3], 54321))
print(getActorID(serverID) + " is up.")

UDPServerSocket.sendto(str.encode(serverID), (contAddress, 54321))

while(True):
    #Receive input
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0].decode('UTF-8')
    address = bytesAddressPair[1]

    #Print out message from forwarder
    output = getActorID(message[6:12]) + ": " + message[18:]
    print("Message recieved from {}".format(output))

    #Send confirmation back to user
    serverHeader = message[6:12] + serverID + serverID
    bytesToSend = str.encode(serverHeader + "Recieved message from " + getActorID(message[6:12]) + "!")
    UDPServerSocket.sendto(bytesToSend, address)
