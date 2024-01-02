# dependencias
import socket
import time
import select
from Conn import *
from utils import *
from Packet import *

#Data
PACKET_SIZE = 512 # tamaño de los paquetes 
WINDOW_SIZE = 5 # tamaño de la ventana deslizante
TIMEOUT = 0.05 # tiempo de la confirmacion del ack

# complementos
log = True

def listen(address: str) -> Conn:
  try:
    ip = parse_address(address) # parsear la dirección IP para el socket
  except ValueError as e:
    raise ValueError(f"Invalid IP address: {address}") from e
  
  conn = Conn(address)
  conn.socket.bind(parse_address(address))  # enlazar el socket a una direccion especifica
  
  if log:
    print(f"Socket bind: {parse_address(address)}")

  return conn

def accept(conn: Conn) -> Conn:
  data, addr = conn.socket.recvfrom(65535)  # recibir hasta 65535 bytes de data

  if log:
    print(f"Received data from {addr}: {data}")

  conn.dataRec[addr] = data
  return conn

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
  while conn.nextSeqNum < len(data):
        while conn.nextSeqNum < conn.base + WINDOW_SIZE:
            packetData = data[conn.nextSeqNum:conn.nextSeqNum + PACKET_SIZE]  # Dividir datos en paquetes
            packet = CreatePacket(conn, packetData)  # Crear el paquete a enviar

            conn.unacked_packets[conn.nextSeqNum] = packet  # Almacenar paquete no confirmado
            SendPacket(conn, packet)  # Enviar paquete
            conn.nextSeqNum += PACKET_SIZE  # Avanzar el número de secuencia

        WaitACK(conn)  # Esperar confirmación de los paquetes enviados

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
        for packet in conn.unacked_packets:
          SendPacket(conn, packet)


def recv(conn: Conn, length: int) -> bytes:
    pass


def close(conn: Conn):
    pass

class ConnException(Exception):
  pass
