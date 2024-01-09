# dependencias
import time
from conn import *
from utils import *
from packet import *
from clock import *
import threading
# manejo de datos
PACKET_SIZE = 512 # tamaño de los paquetes 
WINDOW_SIZE = 5 # tamaño de la ventana deslizante
TIMEOUT = 0.05 # tiempo de la confirmacion del ack

# errores
INVALID_IP_ADDRESS = "Invalid IP address: %s"
FIRST_CONNECT = "Can't send data whithout previous connecting to the server"
CONNECTION_IN_USE = "Connection already in use"

# complementos
log = True

def listen(address: str) -> Conn:
  try:
    ip = parse_address(address) # parsear la dirección IP para el socket

  except ValueError as e:
    raise ValueError(INVALID_IP_ADDRESS %address) from e
  
  conn = Conn(address)
  conn.socket.bind(parse_address(address))  # enlazar el socket a una direccion especifica
  
  if log:
    print(f"Socket bind: {parse_address(address)}")

  return conn

def accept(conn: Conn) -> Conn:
  HandleFlags(conn)
  return conn

def HandleFlags(conn: Conn):
  if conn.state:
    raise ConnException(CONNECTION_IN_USE)
  
  if log:
    print('Waiting data')

  data = conn.socket.recvfrom(PACKET_SIZE)[0][20:]

  if data[:4] == b'\x00\x0f\x00\x0f':
    # 0:token  1:source 2:destination 3:sourcePort 4:destPort 5:SeqNum  6:ACK/7:flags 8:winSize 9:CheckSum 10:data
    pack: list = Unpack(data)
    print(pack)

    if CheckSum(data[:28] + data[32:]) == pack[9]:
      flags = pack[7]
      conn.dest = f'{pack[2]}:{pack[4]}'
      ipSrc, portSrc = parse_address(conn.address)
      ipDest, portDest = parse_address(conn.dest)

      # flags => 1.URG  2.ACK  3.PSH  4.RST  5.SYN  6.FIN
      if flags & (1 << 1): # si el flag SYN esta activo
        time.sleep(4)
        conn.socket.sendto(Packet(ipSrc, ipDest, portSrc, portDest, 0, pack[5] + 1, 18, 
                                        255, b'').CreatePacket(),
                      parse_address(conn.dest))
        conn.expectedNum = pack[5] + 1
        
def dial(address) -> Conn:
  try:
   ip = parse_address(address) # parsear la dirección IP para el socket
   
  except ValueError as e:
     raise ValueError(INVALID_IP_ADDRESS %address) from e
  
  ipDest, portDest = parse_address(address) # ip y puerto del server
  ip = '127.0.0.1' # host ip
  port = 8000 # host port
  pack = Packet(ip, ipDest, port, portDest, 0, 0, 2, 255, b'') # crear el paquete con el flag SYN activado
  conn = Conn(f'{ip}:{port}') # crear la conexion del cliente
  conn.socket.sendto(pack.CreatePacket(), parse_address(f'{ipDest}:{portDest}')) # enviar el paquete al servidor
  time.sleep(3)
  conn = listen(f'{ip}:{port}') # escuchar respuesta del servidor
  
  if log:
    print("Waiting data")

  data, _ = conn.socket.recvfrom(255) # recibir data del servidor
  data = data[20:]
  packData = Unpack(data) # desempaquetar los datos
  
  if log:
    print(packData)
    print('Succesful connection')

  return conn

def send(conn: Conn, data: bytes) -> int:
  ipSrc, portSrc = parse_address(conn.address)
  ipDest, portDest = parse_address(conn.dest)
  fragData = fragment_data(data, PACKET_SIZE)
  seqNum = 0
  ackNum = 0


  for i in range(len(fragData)):
    pack = Packet(ipSrc, ipDest, portSrc, portDest, seqNum, ackNum, 16, PACKET_SIZE, fragData[i])
    conn.socket.sendto(pack.CreatePacket(), parse_address(conn.dest))

    if log:
      print('Waiting data')

    data = recvConf(conn, 1)
    if data == None:
      i = i-1
      continue   #conn.socket.recvfrom(PACKET_SIZE)[0][20:]
    packet = Unpack(data)
    seqNum = packet[6]
    ackNum = packet[5] + 1

  
  return len(data)

def recvConf(conn: Conn, timelimit):
  ipdest, portdest = parse_address(conn.dest)
  conn.sendTime.init(timelimit)
  conn.sendTime.start()
  while True:
    conn.socket.settimeout(timelimit)
    try:
        data = conn.socket.recvfrom(PACKET_SIZE)[0][20:]
    except socket.timeout:
        return (None, None)
    packet = Unpack(data)
    if (packet[2] == portdest):
        return data
    timelimit = timelimit - conn.sendTime.clock()
  
def recv(conn: Conn, length: int, dataSend: bytes = b'') -> bytes:
  dataRec = b''

  if log:
    print('Waiting data')

  while True:
    data = conn.socket.recvfrom(PACKET_SIZE)[0][20:]
    dataRec += data

    if data[:4] == b'\x00\x0f\x00\x0f':
      # 0:token  1:source 2:destination 3:sourcePort 4:destPort 5:seqNum 6:ACK 7:flags 8:winSize 9:CheckSum 10:data
      if len(data) <= length:
        pack: list = Unpack(data)

        if CheckSum(data[:28] + data[32:]) == pack[9]:
          ipSrc, portSrc = parse_address(conn.address)
          ipDest, portDest = parse_address(conn.dest)

          if pack[7] & 1:
            return dataRec
            
          if data[6] == conn.expectedNum: # pack[6] se refiere al ack
            conn.socket.sendto(Packet(ipSrc, ipDest, portSrc, portDest, pack[6], pack[5] + 1, 16, 
                                           PACKET_SIZE, dataSend).CreatePacket(),
                          parse_address(conn.dest))
          
          if(pack[7] & 1): # si se envio  el paquete final el flag FIN activo
            return dataRec

        if dataSend == b'':
          conn.dest = pack[5] + 1

        else:
          conn.dest = pack[5] + len(dataSend)
      
def close(conn: Conn):
  conn.socket.close()

class ConnException(Exception):
  pass



