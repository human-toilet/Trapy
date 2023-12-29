# dependencias
import socket
import ipaddress

class Conn:
  def __init__(self, address, log=False, sock=None):
    if sock is None:
      sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
     
    self.address = address
    self.log = log
    self.socket = sock


def listen(address: str) -> Conn:
  try:
    ip = ipaddress.ip_address(address) # parsear la direccion IP para el socket
  except ValueError as e:
    raise ValueError(f"Invalid IP address: {address}") from e

  conn = Conn(address)
  conn.socket.bind((ipaddress.ip_address(address), 1235))  # enlazar el socket a una direccion especifica
  return conn

def accept(conn) -> Conn:
    pass

class ConnException(Exception):
  pass




def dial(address) -> Conn:
    pass


def send(conn: Conn, data: bytes) -> int:
    pass


def recv(conn: Conn, length: int) -> bytes:
    pass


def close(conn: Conn):
    pass
