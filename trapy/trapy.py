# dependencias
import time
from conn import *
from utils import *
from packet import *
from clock import *
import threading

# manejo de datos
PACKET_SIZE = 512 # tamaño de los paquetes 
TIMEOUT = 3 # tiempo de la confirmacion del ack
WIN_SIZE = 255 # tamaño de la ventana

# errores
INVALID_IP_ADDRESS = "Invalid IP address: %s"
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
  HandleAccept(conn)
  return conn

def HandleAccept(conn: Conn):
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
      conn.dest = f'{pack[1]}:{pack[3]}'
      ipSrc, portSrc = parse_address(conn.address)
      ipDest, portDest = parse_address(conn.dest)

      # flags => 1.URG  2.ACK  3.PSH  4.RST  5.SYN  6.FIN
      if flags & (1 << 1): # si el flag SYN esta activo
        print('Sending data')
        time.sleep(1)
        conn.socket.sendto(Packet(ipSrc, ipDest, portSrc, portDest, 0, pack[5] + 1, 18, 
                                        WIN_SIZE, b'').CreatePacket(),
                      parse_address(conn.dest))
        conn.expectedNum += 1
  
  print('Waiting data')
  data = conn.socket.recvfrom(PACKET_SIZE)[0][20:]
  time.sleep(1)
  pack: list = Unpack(data)
  print(pack)
  
  if pack[5] == conn.expectedNum:
    print('Succesful connection')
        
def dial(address) -> Conn:
  try:
   ip = parse_address(address) # parsear la dirección IP para el socket
   
  except ValueError as e:
     raise ValueError(INVALID_IP_ADDRESS %address) from e
  
  ipDest, portDest = parse_address(address) # ip y puerto del server
  ip = '127.0.0.2' # host ip
  port = 8000 # host port
  pack = Packet(ip, ipDest, port, portDest, 0, 0, 2, WIN_SIZE, b'') # crear el paquete con el flag SYN activado
  conn = Conn(f'{ip}:{port}') # crear la conexion del cliente
  print('Sending data')
  conn.socket.sendto(pack.CreatePacket(), parse_address(f'{ipDest}:{portDest}')) # enviar el paquete al servidor
  conn = listen(f'{ip}:{port}') # escuchar respuesta del servidor
  
  if log:
    print("Waiting data")

  data, _ = conn.socket.recvfrom(PACKET_SIZE) # recibir data del servidor
  data = data[20:]
  packData = Unpack(data) # desempaquetar los datos
  conn.dest = f'{ipDest}:{portDest}'

  if log:
    print(packData)

  if packData[7] == 18 and packData[5] == 0:
    print('Sending data')
    time.sleep(1)
    conn.socket.sendto(Packet(ip, ipDest, port, portDest, packData[6], packData[5] + 1, 16, WIN_SIZE, b'').CreatePacket(),
                  parse_address(conn.dest))
  
  time.sleep(1)
  print('Succesful connection')

  return conn

def send(conn: Conn, data: bytes) -> int:
  ipSrc, portSrc = parse_address(conn.address)
  ipDest, portDest = parse_address(conn.dest)
  fragData = fragment_data(data, PACKET_SIZE)
  seqNum = 0
  ackNum = 0

  for i in range(len(fragData)):
    fin = i == len(fragData) - 1 
    finFlag = 0

    if fin :
      finFlag = 17
    
    else:
      finFlag = 16

    pack = Packet(ipSrc, ipDest, portSrc, portDest, seqNum, ackNum, finFlag, len(fragData[i]), fragData[i])
    print('Sending data')
    conn.socket.sendto(pack.CreatePacket(), parse_address(conn.dest))

    if log:
      print('Waiting data')

    dat = recvConf(conn, TIMEOUT)
    if dat == None:
      i = i-1
      continue   #conn.socket.recvfrom(PACKET_SIZE)[0][20:]

    packet = Unpack(dat)
    print(packet)

    if packet[7] & 1: # ya no se pueden enviar mas datos
      close(conn)
      return PACKET_SIZE * i

    if packet[5] != ackNum: # si el numero de secuencia del paquete que entro non coincide
      i -= 1                # con el numero de ack debemos reenviar el paquete
      continue

    seqNum = packet[6]
    ackNum = packet[5] + 1

  return len(data)

def recvConf(conn: Conn, timelimit):
  ipdest, portdest = parse_address(conn.dest)
  conn.sendTime = Timer(timelimit)
  conn.sendTime.start()
  while True:
    conn.socket.settimeout(timelimit)
    try:
        data = conn.socket.recvfrom(PACKET_SIZE)[0][20:]
    except socket.timeout:
        return None
    packet = Unpack(data)
    
    if (packet[3] == portdest):
        return data
    timelimit = timelimit - conn.sendTime.clock()
  
def recv(conn: Conn, length: int, dataSend: bytes = b'') -> bytes:
  dataRec = b''

  if log:
    print('Waiting data')
  
  ipSrc, portSrc = parse_address(conn.address)
  ipDest, portDest = parse_address(conn.dest)
  expectedACK = 0

  while True:
    data = conn.socket.recvfrom(PACKET_SIZE)[0][20:]
    time.sleep(1)

    if data[:4] == b'\x00\x0f\x00\x0f':
      # 0:token  1:source 2:destination 3:sourcePort 4:destPort 5:seqNum 6:ACK 7:flags 8:winSize 9:CheckSum 10:data
      if len(dataRec) <= length:
        pack: list = Unpack(data)
        dataRec += pack[10]
        print(pack)

        if CheckSum(data[:28] + data[32:]) == pack[9]:
          if(pack[7] & 1): # si se envio en el paquete final el flag FIN activo
            print('Sending data')
            conn.socket.sendto(Packet(ipSrc, ipDest, portSrc, portDest, 0, 0, 1, 
                                  WIN_SIZE, b'fin').CreatePacket(),
                          parse_address(conn.dest))
            close(conn)
            return dataRec
            
          if data[6] == expectedACK: # pack[6] se refiere al ack
            print('Sending data')
            conn.socket.sendto(Packet(ipSrc, ipDest, portSrc, portDest, pack[6], pack[5] + 1, 16, 
                                           WIN_SIZE, dataSend).CreatePacket(),
                          parse_address(conn.dest))
            expectedACK += 1
          
        if dataSend == b'':
          conn.dest = pack[5] + 1

        else:
          conn.dest = pack[5] + len(dataSend)
      
      else:
        packet = Packet(ipSrc, ipDest, portSrc, portDest, 0, 0, 1, 0, b'buffer is full')
        conn.socket.sendto(packet, parse_address(conn.dest))
      
def close(conn: Conn):
  print('Connection closed')
  conn.socket.close()

class ConnException(Exception):
  pass



