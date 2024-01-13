# dependencias
import socket
import struct
from conn import Conn
from utils import *

class Packet:
  def __init__(self, sourceAddress: str, destinationAddress: str, sourcePort: int, destinationPort: int, seqNumber: int, ack: int, flags: int, winSize: int, data=b''):
    self.sourceAddress = sourceAddress
    self.destinationAddress = destinationAddress
    self.sourcePort = sourcePort
    self.destinationPort = destinationPort
    self.seqNumber = seqNumber
    self.ack = ack
    self.flags = flags
    self.winSize = winSize
    self.data = data

  # creacion del paquete en formato de bytes para enviar
  def CreatePacket(self) -> bytes:
    ipHeader = b'\x00\x0f\x00\x0f'  # token
    ipHeader += socket.inet_aton(self.sourceAddress)
    ipHeader += socket.inet_aton(self.destinationAddress)
    tcpHeaderNocheckSum: bytes = struct.pack('!2h2i2h', self.sourcePort, self.destinationPort,
                                     self.seqNumber, self.ack, self.flags, self.winSize)
    tcpHeader: bytes = struct.pack('!2h2i2hi', self.sourcePort, self.destinationPort,
                                     self.seqNumber, self.ack, self.flags, self.winSize, CheckSum(ipHeader + tcpHeaderNocheckSum + self.data))
    return ipHeader + tcpHeader + self.data

