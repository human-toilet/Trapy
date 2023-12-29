# dependencias
import socket
from utils import parse_address

# complementos
log = True

class Conn:
  def __init__(self, address, log=True, sock=None):
    if sock is None:
      sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
     
    self.address = address
    self.socket = sock
    self.dataRec = None

def listen(address: str) -> Conn:
  try:
    ip = parse_address(address) # parsear la direccion IP para el socket
  except ValueError as e:
    raise ValueError(f"Invalid IP address: {address}") from e

  conn = Conn(address)
  conn.socket.bind(parse_address(address))  # enlazar el socket a una direccion especifica
  
  if log:
    print(f"Socket bind: {parse_address(address)}")

  return conn

def accept(conn: Conn) -> Conn:
  data, addr = conn.socket.recvfrom(1024)  # recibir hasta 1024 bytes de data

  if log:
    print(f"Received data from {addr}: {data}")

  conn.dataRec = data
  return conn

def dial(address) -> Conn:
    pass


def send(conn: Conn, data: bytes) -> int:
    pass


def recv(conn: Conn, length: int) -> bytes:
    pass


def close(conn: Conn):
    pass

class ConnException(Exception):
  pass
