import socket

class Conn:
  def __init__(self, address, sock=None):
    if sock is None:
      sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    
    self.address = address
    self.dest: str = None
    self.state = False
    self.socket = sock
    self.base: int = 0  # puntero base de la ventana
    self.expectedNum: int = 0  # siguiente número de secuencia a enviar
    self.unackedPackets: dict = {}  # almacenar paquetes no confirmados
    self.dataRec: str = ''