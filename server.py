import asyncore
import mimetypes
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


class HTTPHandler(asyncore.dispatcher_with_send):
    def handle_read(self):
        data = self.recv(1024)
        if data:
            response = self._process_request(data)
            self.send(response)

    def _create_response_header(self, protocol, response_code, content_type, content_length):
        return protocol + ' ' + response_code + '\n' + \
            'Date: ' + current_date_time() + '\n' + \
            'Connection: keep-alive' + '\n' + \
            'Server: simple-server' + '\n' + \
            'Accept-Ranges: bytes' + '\n' + \
            'Content-Type: ' + content_type + '\n' + \
            'Content-Length: ' + str(content_length)

    def _process_request(self, data):
        try:
            verb, req_uri, protocol = [token.strip() for token in data.splitlines()[0].split(' ')]
        except ValueError:
            print 'Invalid HTTP request: ', data
            return data

        if verb == 'GET':
            uri = req_uri[1:]
            if not uri:
                uri = 'index.html'
            uri_path = os.path.join(os.getcwd(), uri)
            if os.path.exists(uri_path):
                content_length = os.path.getsize(uri_path)
                with open(uri_path, 'rb') as response_file:
                    _, extension = os.path.splitext(uri_path)
                    content_type = mimetypes.types_map[extension]
                    response = self._create_response_header(protocol, '200 OK', content_type, content_length) + \
                        '\n\n' + response_file.read()
            else:
                # Construct 404 response
                response_str = 'Cannot GET %s' % req_uri
                content_length = len(response_str)
                content_type = mimetypes.types_map['.txt']
                response = self._create_response_header(protocol, '404 Not Found', content_type, content_length) + \
                    '\n\n' + response_str
            return response
        else:
            return data


class Server(asyncore.dispatcher):
    ''' Server '''

    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.ip = '127.0.0.1'
        self.port = 5005
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((self.ip, self.port))
        self.listen(5)

    def start(self):
        asyncore.loop()

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            client, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            handler = HTTPHandler(client)

    def stop(self, signal, handler):
        self.close()
        sys.exit(0)


if __name__ == '__main__':
    server = Server()
    signal.signal(signal.SIGINT, server.stop)
    server.start()

