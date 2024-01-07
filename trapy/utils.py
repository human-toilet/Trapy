def parse_address(address):
  host, port = address.split(':')
  
  if host == '':
      host = 'localhost'
      
  return host, int(port)

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
      if sum > 0xffff:
          sum = (sum & 0xffff) + 1

  sum = ~sum & 0xffff # Complementar el resultado final para obtener el checksum en complemento a uno
  return sum
