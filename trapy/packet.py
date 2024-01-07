# dependencias
import socket
import struct
import logging
from Conn import Conn
from utils import parse_address

def Unpack(packet: bytes) -> list:
  try:
    ipHeader = packet[:12]  # encabezado IP (los primeros 12 bytes)
    tcpHeader = packet[12:32]  # encabezado TCP (bytes 12 a 32)
    sourceIp = socket.inet_ntoa(ipHeader[4:8])  # dirección IP de origen
    destIp = socket.inet_ntoa(ipHeader[8:12])  # dirección IP de destino
    tcpData = struct.unpack('!HHLLBBHHH', tcpHeader)  # desempaquetar encabezado TCP
    unpackedData = [packet[:4], sourceIp, destIp] + list(tcpData) + [packet[32:]] # combinar información del encabezado IP y TCP en una lista
    return unpackedData
  
  except Exception as err:
    logging.error(err)
    return None

def SendPacket(conn: Conn, packet: bytes):
  conn.socket.sendto(packet, parse_address(conn.address))

def CreatePacket(conn: Conn, packetData: bytes) -> bytes:
  seqNumber = conn.nextSeqNum
  packet = struct.pack('I', seqNumber) + packetData
  return packet