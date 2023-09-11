#Author: Peter Gutstein
import socket
import sys
import multiprocessing
import time
import pickle

def onSameSubnet(ipOne, ipTwo):
    ipOneParts =  ipOne.split(".", 2)
    ipTwoParts =  ipTwo.split(".", 2)
    return ((ipOneParts[0] == ipTwoParts[0]) and (ipOneParts[1] == ipTwoParts[1]))

def getActorID(id):
    if id[0:3] == "000":
        return "User" + id[3:6]
    elif id[0:3] == "111":
        return "Forwarder" + id[3:6]
    elif id[0:3] == "222":
        return "Server" + id[3:6]
