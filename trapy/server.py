from trapy import *

address = '127.0.0.1:8888'
conn = listen(address)
accept(conn) 
recv(conn, 5000) 
