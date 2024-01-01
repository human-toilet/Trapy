# dependencias
import socket
import struct
import logging

def unpack(packet: bytes) -> list:
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

def checkSum(data: bytes) -> int:
  sum = 0

  # Si la longitud de los datos es impar, se agrega un byte nulo al final
  if len(data) % 2 != 0:
      data += b'\x00'

  for i in range(0, len(data), 2):
      # Obtener los bytes adyacentes y combinarlos en un número de 16 bits
      word = (data[i] << 8) + data[i + 1]
      sum += word

      # Verificar si hay desbordamiento de bits
      if checksum > 0xffff:
          sum = (sum & 0xffff) + 1

  checksum = ~sum & 0xffff # Complementar el resultado final para obtener el checksum en complemento a uno
  return sum