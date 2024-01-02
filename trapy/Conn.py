import socket

class Conn:
  def __init__(self, address, sock=None):
    if sock is None:
      sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
     
    self.address = address
    self.socket = sock
    self.base = 0  # puntero base de la ventana
    self.nextSeqNum = 0  # siguiente número de secuencia a enviar
    self.unacked_packets = []  # almacenar paquetes no confirmados