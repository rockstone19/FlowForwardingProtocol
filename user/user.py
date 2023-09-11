#Author: Peter Gutstein
from generalFunctions import *

#Important variables
bufferSize = 65507

#Get information from docker-compose file
userID = sys.argv[1]
endPointID = sys.argv[2]
forwardAddressPort = (sys.argv[3], 54321)
contAddress = sys.argv[4]
#Have user wait (helps with terminal output & ensuring nothing breaks)
time.sleep(2)

#Create the user's socket and bind it to IP & port
UDPUserSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPUserSocket.bind((sys.argv[5], 54321))
print(getActorID(userID) + " is up.")

#Send message to controller to set user up with controller
UDPUserSocket.sendto(str.encode(userID), (contAddress, 54321))

#Have user wait (helps with terminal output & ensuring nothing breaks)
time.sleep(4)

#Send message to forwarder
header = endPointID + userID + userID
bytesToSend = str.encode(header + "Hello from {}!".format(getActorID(userID)))
UDPUserSocket.sendto(bytesToSend, forwardAddressPort)

#Receive message and print it
while True:
    bytesAddressPair = UDPUserSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0].decode('UTF-8')
    output = getActorID(message[6:12]) + ": " + message[18:]
    print("Message received from {}".format(output))
