import socket
import struct
import logging

def parse_address(address):
  host, port = address.split(':')
  
  if host == '':
      host = 'localhost'
      
  return host, int(port)

def CheckSum(data: bytes) -> int:
  sum = 0

  # Si la longitud de los datos es impar, se agrega un byte nulo al final
  if len(data) % 2 != 0:
      data += b'\x00'

  for i in range(0, len(data), 2):
      # Obtener los bytes adyacentes y combinarlos en un número de 16 bits
      word = (data[i] << 8) + data[i + 1]
      sum += word

      # Verificar si hay desbordamiento de bits
      if sum > 0xffff:
          sum = (sum & 0xffff) + 1

  sum = ~sum & 0xffff # Complementar el resultado final para obtener el checksum en complemento a uno
  return sum

def Unpack(packet: bytes) -> list:
  try:
    tcpHeader = struct.unpack('!2h2i2hi', packet[12:32])
    pack = [
        packet[0:4], # token de verificacion
        socket.inet_ntoa(packet[4:8]), # ip de origen
        socket.inet_ntoa(packet[8:12]), # ip de destino
    ] + list(tcpHeader)
    pack.append(packet[32:]) # datos recibidos
    return pack
  
  except Exception as err:
      logging.error(err)

  return None

def fragment_data(data: bytes, max_data_size: int):
    fragmented_data = []
    fd_size = 0
    while fd_size < len(data):
        next_position = min(fd_size + max_data_size, len(data))
        fragmented_data.append(data[fd_size:next_position])
        fd_size = next_position
    return fragmented_data