import os
import signal
import socket
import sys

from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime


def current_date_time():
    timestamp = mktime(datetime.now().timetuple())
    return format_date_time(timestamp)


def create_response_header(protocol, response_code, response_size):
    return protocol + ' ' + response_code + '\n' + \
        'Date: ' + current_date_time() + '\n' + \
        'Connection: keep-alive' + '\n' + \
        'Server: simple-server' + '\n' + \
        'Accept-Ranges: bytes' + '\n' + \
        'Content-Type: text/html; charset=UTF-8' + '\n' + \
        'Content-Length: ' + str(response_size) + '\n'


def process_request(data, conn):
    verb, req_uri, protocol = [token.strip() for token in data.splitlines()[0].split(' ')]
    if verb == 'GET':
        uri = req_uri[1:]
        if not uri:
            uri = 'index.html'
        uri_path = os.path.join(os.getcwd(), uri)
        if os.path.exists(uri_path):
            content_length = os.path.getsize(uri_path)
            with open(uri_path, 'r') as response_file:
                response = create_response_header(protocol, '200 OK', content_length) + \
                    '\n\n' + response_file.read()
        else:
            # Construct 404 response
            response_str = 'Cannot GET ' + req_uri
            content_length = len(response_str)
            response = create_response_header(protocol, '404 Not Found', content_length) + \
                '\n\n' + response_str
        conn.send(response)
    else:
        conn.send(data)


class Server:
    ''' Server '''

    def __init__(self):
        self.ip = '127.0.0.1'
        self.port = 5005
        self.buf_size = 1024


    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(1)

        while True:
            client, addr = self.socket.accept()
            print 'Connection address:', addr
            data = client.recv(self.buf_size)
            if not data:
                break
            print 'Received data from client: ', data
            process_request(data, client)
            client.close()

    def stop(self, signal, handler):
        self.socket.shutdown(socket.SHUT_RDWR)
        sys.exit(0)


if __name__ == '__main__':
    server = Server()
    signal.signal(signal.SIGINT, server.stop)
    server.start()

