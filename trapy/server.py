from trapy import *

"""
address = '127.0.0.1:8888'
conn = listen(address)
accept(conn)  
"""
address = '127.0.0.1:8888'
conn = listen(address)
recv(conn, 7788)