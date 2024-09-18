import socket

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('0.0.0.0', 4000))
serversocket.listen(5) # become a server socket, maximum 5 connections
while True:
    connection, address = serversocket.accept()
    buf = connection.recv(64)
    if len(buf) > 0:
        #print(address, buf)
        print(buf.decode('utf-8'))

