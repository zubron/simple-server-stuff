import socket

ip = '127.0.0.1'
port = 5005
buf_size = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((ip, port))
s.listen(1)

conn, addr = s.accept()
print 'Connection address:', addr
while True:
    data = conn.recv(buf_size)
    if not data:
        break
    print 'Received data from client: ', data
    conn.send(data)
conn.close()