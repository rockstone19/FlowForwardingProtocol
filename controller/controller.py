#Author: Peter Gutstein
from generalFunctions import *

#Add edges to graph
def addEdge(graph, node1, node2):
    node1Edges = graph[node1] #add node2 to node1's entry in graph
    node1Edges.append(node2)
    graph[node1] = node1Edges
    node2Edges = graph[node2] #add node1 to node2's entry in graph
    node2Edges.append(node1)
    graph[node2] = node2Edges

#Add address to forwarding table
def addAddress(forwardTable, id, address, graph):
    if id not in forwardTable: #create entries for actor if not already registered
        forwardTable[id] = []
        graph[id] = []
    currentList = forwardTable[id]  #Add address to fTable entry for actor
    currentList.append(address[0])
    forwardTable[id] = currentList

#Handle when an actor declares itself to the controller
def declare(forwardTable, id, address, graph):
    addAddress(forwardTable, id, address, graph)
    #Add new connecting edges to the graph
    tempTable = dict(forwardTable)
    ip = address[0]
    for id2 in tempTable:
        ipList = tempTable[id2]
        for destIP in ipList:
            if onSameSubnet(ip, destIP) and (ip != destIP):
                addEdge(graph, id, id2)

#Listen for requests and process them
def listen(socket, forwardTable, forwardTableMutex, graph):
    try:
        while True:
            bytesAddressPair = socket.recvfrom(bufferSize)
            message = bytesAddressPair[0].decode('UTF-8')
            address = bytesAddressPair[1]

            if len(message) == 6:       #Register actor
                forwardTableMutex.acquire()
                declare(forwardTable, message, address, graph)
                forwardTableMutex.release()
            elif message[0] == "F":     #Get forwarding table and send it over
               encodedTable = pickle.dumps(dict(forwardTable))
               socket.sendto(encodedTable, address)
            elif message[0] == "G":     #Get graph and send it over
               encodedGraph = pickle.dumps(dict(graph))
               socket.sendto(encodedGraph, address)
    except:
        print("ERROR: Please try again")

#Set up important variables
bufferSize = 65507
contManager = multiprocessing.Manager()
graph = contManager.dict()
forwardTable = contManager.dict()
forwardTableMutex = contManager.Lock()

#Declare sockets
controllerSockets = []
for i in range(1, len(sys.argv)):
    UDPContSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPContSocket.bind((sys.argv[i], 54321))
    controllerSockets.append(UDPContSocket)
print("Controller is up!")

#Run the controller on all sockets
for socketNum in range(0, len(controllerSockets) - 1):
    try:
        socket = controllerSockets[socketNum]
        time.sleep(0.1)
        function = multiprocessing.Process(target=listen,args=[socket, forwardTable, forwardTableMutex, graph])
        function.start()
    except:
        print("ERROR: Restart program")
        continue
try:
    time.sleep(0.1)
    listen(controllerSockets[len(controllerSockets) - 1], forwardTable, forwardTableMutex, graph)
except:
    print("ERROR: Restart program. Last socket failed")
