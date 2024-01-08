# dependencias
import socket
import time
import select
from Conn import *
from utils import *
from packet import *

# manejo de datos
PACKET_SIZE = 512 # tamaño de los paquetes 
WINDOW_SIZE = 5 # tamaño de la ventana deslizante
TIMEOUT = 0.05 # tiempo de la confirmacion del ack

# errores
INVALID_IP_ADDRESS = "Invalid IP address: %s"
FIRST_CALL_ACCEPT = "First call accept with %s"
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
  
  data = conn.socket.recvfrom(PACKET_SIZE)[0][20:]

  if data[:4] == b'\x00\x0f\x00\x0f':
    # 0:token  1:source 2:destination 3:sourcePort 4:destPort 5:total 6:ACK/SeqNum 7:flags 8:winSize 9:CheckSum 10:data
    pack: list = Unpack(data)

    if CheckSum(data[:28] + data[32:]) == pack[9]:
      flags = pack[7]

      if flags & (1 << 3): # si el flag SYN esta activo
        conn.socket.sendto(Packet(pack[1], pack[2], pack[3], pack[4], 0, 0, 1 << 6, 
                                        WINDOW_SIZE, b'').CreatePacket(),
                      parse_address(f'{pack[2]}:{pack[4]}'))
      
      elif flags & (1 << 6): # si el flag ACK esta activo
        if conn.seqNum <= pack[6]:
          conn.seqNum = pack[6] + 1
        
def dial(address) -> Conn:
  try:
    ip = parse_address(address) # parsear la dirección IP para el socket

  except ValueError as e:
    raise ValueError(f"Invalid IP address: {address}") from e
  
  sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
  conn = Conn(address, sock=sock)
  
  # conectar el socket a la dirección remota
  conn.socket.connect(parse_address(address))
  
  return conn

def send(conn: Conn, data: bytes) -> int:
  """while conn.nextSeqNum < len(data):
    while conn.nextSeqNum < conn.base + WINDOW_SIZE:
      packetData = data[conn.nextSeqNum:conn.nextSeqNum + PACKET_SIZE]  # Dividir datos en paquetes
      packet = CreatePacket(conn, packetData)  # Crear el paquete a enviar
      conn.unackedPackets[conn.nextSeqNum] = packet  # Almacenar paquete no confirmado
      SendPacket(conn, packet)  # Enviar paquete
      conn.nextSeqNum += PACKET_SIZE  # Avanzar el número de secuenci

    WaitACK(conn)  # Esperar confirmación de los paquetes enviado

  return len(data)

def WaitACK(conn: Conn):
  start_time = time.time()  # Tiempo de inicio para el temporizador de espera

  while time.time() - start_time < TIMEOUT:  # Espera durante un tiempo máximo
      ready = select.select([conn.socket], [], [], TIMEOUT)
      if ready[0]:  # Si hay algo listo para leer en el socket
        data, _ = conn.socket.recvfrom(PACKET_SIZE)
        return
      else:
        # Si no se recibe ACK dentro del tiempo TIMEOUT, reenviar paquetes no confirmados
        for packet in conn.unackedPackets:
          SendPacket(conn, packet)
"""
def recv(conn: Conn, length: int) -> bytes:
  """received_data = b""

  while len(received_data) < length:
    packet, _ = conn.socket.recvfrom(PACKET_SIZE)
    header = packet[:4]
    seq_number = struct.unpack("!I", header)[0]
    data = packet[4:]

    if seq_number == conn.nextSeqNum:
        received_data += data
        conn.nextSeqNum += len(data) 
        # Enviar ACK por el paquete recibido
        send_ack(conn, seq_number + len(data))

  return received_data[:length]"""

def close(conn: Conn):
  conn.socket.close()

class ConnException(Exception):
  pass




