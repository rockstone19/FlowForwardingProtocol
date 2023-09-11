#Author: Peter Gutstein
from generalFunctions import *

def findNextIP(sender, reciever, forwardTable):
    tempTable = dict(forwardTable)
    for ipSender in tempTable[sender]:
        for ipReciever in tempTable[reciever]:
            if onSameSubnet(ipSender, ipReciever):
                return ipReciever

def findPath(endPointID, senderID, lastSenderID, graph, path = []):
    #Prepare starting path & base case for recursion
    path = path + [senderID]
    if senderID == endPointID:
        return path
    shortestPath = []
    shortPathSet = False

    #If graph empty, return None
    if len(graph) == 0:
        return None
    #Go into each senderNode node and recursively try to find a path
    for node in graph.get(senderID):
        if node != lastSenderID and node not in path:
            pathToEnd = findPath(endPointID, node, lastSenderID, graph, path)
            if pathToEnd != None:   #If a path is found, update shortestPath
                if not shortPathSet:
                    shortestPath = pathToEnd
                    shortPathSet = True
                if len(pathToEnd) < len(shortestPath):
                    shortestPath = pathToEnd
    if shortestPath != []:     #If a path exists
        return shortestPath
    else:#If no path from node to endpoint, return none (used in recursion/bad graph)
        return None

def forward(socket, graph, forwardTable, fTableMutex):
    #try:
        while True:
            #Receive from something else & print confirmation
            bytesAddressPair = socket.recvfrom(bufferSize)
            fTableMutex.acquire()
            #Break header down into components
            message = bytesAddressPair[0].decode('UTF-8')
            address = bytesAddressPair[1]
            endPointID = message[0:6]
            senderID = message[6:12]
            lastSenderID = message[12:18]
            restOfMessage = message[18:]
            print("Recieved a message from " + getActorID(senderID) + " going to " + getActorID(endPointID))

            #Figure out where to go from graph
            nextNodePath = findPath(endPointID, forwarderID, lastSenderID, graph)
            #If can't find from graph, get new graph from controller
            if(type(nextNodePath) == type(None)):
                print("Couldn't find path: contacting controller")
                #Get the address of the controller for the socket and request graph
                if onSameSubnet(socket.getsockname()[0], contAddresses[0]):
                    socket.sendto(str.encode("G"), (contAddresses[0], 54321))
                else:
                    socket.sendto(str.encode("G"), (contAddresses[1], 54321))
                bytesAddressPair = socket.recvfrom(bufferSize)
                graph = pickle.loads(bytesAddressPair[0])

                #Request fTable
                socket.sendto(str.encode("F"), bytesAddressPair[1])
                bytesAddressPair = socket.recvfrom(bufferSize)
                forwardTable = pickle.loads(bytesAddressPair[0])
                nextNodePath = findPath(endPointID, forwarderID, lastSenderID, graph)

            #Figure out where to go from nextNode
            addressToForwardTo = (findNextIP(nextNodePath[0], nextNodePath[1], forwardTable), 54321)
            #Find correct socket to send from
            senderSocket = socket
            for s in forwarderSockets:
                socketIP = s.getsockname()[0]
                if onSameSubnet(socketIP, addressToForwardTo[0]):
                    senderSocket = s

            #Send message from senderSocket to next place
            print("Forwarding message received from {}".format(getActorID(lastSenderID)) + " to {}".format(getActorID(nextNodePath[1])))
            bytesToSend = endPointID + senderID + forwarderID + restOfMessage
            senderSocket.sendto(str.encode(bytesToSend), addressToForwardTo)
            fTableMutex.release()
    #except:
    #    print("ERROR: Forwarding issue")

#Wait to set up, minimizes need to ask controller for new graph/fTable
time.sleep(4)

#Important variables
bufferSize = 65507
forwardManager = multiprocessing.Manager()
graph = forwardManager.dict()
forwardTable = forwardManager.dict()
fTableMutex = forwardManager.Lock()

#Get information from docker-compose file
forwarderID = sys.argv[1]
contAddresses = [sys.argv[2], sys.argv[3]]

#Create sockets
socketOne = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socketTwo = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socketOne.bind((sys.argv[4], 54321))
socketTwo.bind((sys.argv[5], 54321))
forwarderSockets = [socketOne, socketTwo]
print(getActorID(forwarderID) + " is up.")

#Declare socket 1
fTableMutex.acquire()
forwarderSockets[0].sendto(str.encode(forwarderID), (contAddresses[0], 54321))
fTableMutex.release()

#Declare socket 2 & have it request graph and fTable
fTableMutex.acquire()
forwarderSockets[1].sendto(str.encode(forwarderID), (contAddresses[1], 54321))

#Request graph from the controller after a small delat (allows delcare to work safely)
time.sleep(1)
forwarderSockets[1].sendto(str.encode("G"), (contAddresses[1], 54321))
bytesAddressPair = forwarderSockets[1].recvfrom(bufferSize)
graph = pickle.loads(bytesAddressPair[0])

#Request fTable from the controller
forwarderSockets[1].sendto(str.encode("F"), (contAddresses[1], 54321))
bytesAddressPair = forwarderSockets[1].recvfrom(bufferSize)
forwardTable = pickle.loads(bytesAddressPair[0])
fTableMutex.release()

#Run process on both sockets
function = multiprocessing.Process(target=forward,args=[forwarderSockets[0], graph, forwardTable, fTableMutex])
function.start()
forward(forwarderSockets[1], graph, forwardTable, fTableMutex)
