import socket
from clock import *

class Conn:
  def __init__(self, address, sock=None, timeOut=-1):
    if sock is None:
      sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP) # crea el socket
    
    self.address = address # ip y puerto del sevidor
    self.dest: str = None # ip y puerto del cliente
    self.state = False # si ya esta enlazado a un cliente
    self.sendTime = Timer(timeOut) # manejar los tiempos de espera
    self.socket = sock
    self.expectedNum: int = 0  # siguiente número de secuencia a enviar