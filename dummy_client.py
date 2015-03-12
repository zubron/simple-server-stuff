import socket

ip = '127.0.0.1'
port = 5005
buf_size = 1024
msg = 'Hello, World!'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip, port))
s.send(msg)
data = s.recv(buf_size)
s.close()

print 'Received data from server: ', data
