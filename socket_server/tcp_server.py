#! /usr/bin/env python
# coding=utf-8

from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop


class Connection(object):
    clients = set()

    def __init__(self, stream, address):
        Connection.clients.add(self)
        self._stream = stream
        self._address = address
        self._stream.set_close_callback(self.on_close)
        self.read_message()
        print "A new user has entered the chat room.", address

    def read_message(self):
        self._stream.read_bytes(4096, self.broadcast_messages, partial=True)

    def broadcast_messages(self, data):
        print "User said:", data[:-1], self._address
        for conn in Connection.clients:
            conn.send_message(data)
        self.read_message()

    def send_message(self, data):
        self._stream.write(data)

    def on_close(self):
        print "A user has left the chat room.", self._address
        Connection.clients.remove(self)


class ChatServer(TCPServer):
    def handle_stream(self, stream, address):
        print "New connection :", address, stream
        Connection(stream, address)
        print "connection num is:", len(Connection.clients)


if __name__ == '__main__':
    print "Server start ......"
    server = ChatServer()
    server.listen(9090)
    IOLoop.instance().start()
