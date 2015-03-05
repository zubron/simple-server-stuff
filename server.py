import os
import socket

from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime

ip = '127.0.0.1'
port = 5005
buf_size = 1024


def current_date_time():
    timestamp = mktime(datetime.now().timetuple())
    return format_date_time(timestamp)


def create_response_header(protocol, response_size):
    return protocol + ' 200 OK' + '\n' + \
        'Date: ' + current_date_time() + '\n' + \
        'Connection: close' + '\n' + \
        'Server: simple-server' + '\n' + \
        'Accept-Ranges: bytes' + '\n' + \
        'Content-Type: text/html; charset=UTF-8' + '\n' + \
        'Content-Length: ' + str(response_size) + '\n'


def process_request(data, conn):
    verb, uri, protocol = [token.strip() for token in data.splitlines()[0].split(' ')]
    if verb == 'GET' and uri == '/':
        response_filename = 'index.html'
        content_length = os.path.getsize(response_filename)
        with open(response_filename, 'r') as response_file:
            response = create_response_header(protocol, content_length) + \
                '\n\n' + response_file.read()
        conn.send(response)
    else:
        conn.send(data)


def run_server():
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
        process_request(data, conn)
    conn.close()


if __name__ == '__main__':
    run_server()
