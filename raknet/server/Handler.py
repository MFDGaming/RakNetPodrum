from ..GeneralVariables import GeneralVariables
from ..protocol.IncompatibleProtocol import IncompatibleProtocol
from ..protocol.OpenConnectionReply1 import OpenConnectionReply1
from ..protocol.OpenConnectionReply2 import OpenConnectionReply2
from ..protocol.OpenConnectionRequest1 import OpenConnectionRequest1
from ..protocol.OpenConnectionRequest2 import OpenConnectionRequest2
from ..protocol.UnconnectedPing import UnconnectedPing
from ..protocol.UnconnectedPingOpenConnections import UnconnectedPingOpenConnections
from ..protocol.UnconnectedPong import UnconnectedPong
from ..utils.InternetAddress import InternetAddress

class Handler:
    def handleUnconnectedPing(self, data):
        packet = UnconnectedPing()
        packet.buffer = data
        packet.decode()
        newPacket = UnconnectedPong()
        newPacket.time = packet.time
        newPacket.serverGuid = GeneralVariables.options["guid"]
        newPacket.serverName = GeneralVariables.options["name"]
        return newPacket
        
    def handleUnconnectedPingOpenConnections(self, data):
        packet = UnconnectedPingOpenConnections()
        packet.buffer = data
        packet.decode()
        newPacket = UnconnectedPong()
        newPacket.time = packet.time
        newPacket.serverGuid = GeneralVariables.options["guid"]
        newPacket.serverName = GeneralVariables.options["name"]
        return newPacket
    
    def handleOpenConnectionRequest1(self, data):
        packet = OpenConnectionRequest1()
        packet.buffer = data
        packet.decode()
        print(f"Your protocol version is {str(packet.protocolVersion)}.")
        if packet.protocolVersion not in GeneralVariables.options["acceptedProtocolVersions"]:
             newPacket = IncompatibleProtocol()
             newPacket.protocolVersion = packet.protocolVersion
             newPacket.serverGuid = GeneralVariables.options["guid"]
             return newPacket
        newPacket = OpenConnectionReply1()
        newPacket.serverGuid = GeneralVariables.options["guid"]
        newPacket.useSecurity = 0
        newPacket.mtuSize = packet.mtuSize
        return newPacket
    
    def handleOpenConnectionRequest2(self, data, address):
        packet = OpenConnectionRequest2()
        packet.buffer = data
        packet.decode()
        newPacket = OpenConnectionReply2()
        newPacket.serverGuid = GeneralVariables.options["guid"]
        newPacket.clientAddress = address
        newPacket.mtuSize = packet.mtuSize
        newPacket.useSecurity = 0
        GeneralVariables.server.addConnection(address, packet.mtuSize)
        return newPacket
    
    def handle(self, data, address):
        id = data[0]
        if GeneralVariables.options["debug"]:
            print(GeneralVariables.packetNames[id])
        if GeneralVariables.server.getConnection():
            pass # Todo Custom Packets / Data Packets
        elif id == GeneralVariables.packetIds["UnconnectedPing"]:
            newPacket = self.handleUnconnectedPing(data)
            GeneralVariables.server.sendPacket(newPacket, address[0], address[1])
        elif id == GeneralVariables.packetIds["UnconnectedPingOpenConnections"]:
            newPacket = self.handleUnconnectedPingOpenConnections(data)
            GeneralVariables.server.sendPacket(newPacket, address[0], address[1])
        elif id == GeneralVariables.packetIds["OpenConnectionRequest1"]:
            newPacket = self.handleOpenConnectionRequest1(data)
            GeneralVariables.server.sendPacket(newPacket, address[0], address[1])
        elif id == GeneralVariables.packetIds["OpenConnectionRequest2"]:
            newPacket = self.handleOpenConnectionRequest2(data, InternetAddress(address[0], address[1], 4))
            GeneralVariables.server.sendPacket(newPacket, address[0], address[1])
