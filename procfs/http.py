import argparse
import json
import os
import sys
import string
import socket

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

from procfs import Proc
from procfs.core import ProcDirectory
from procfs.core import ProcessFile
from procfs.core import File

from procfs.exceptions import DoesNotExist

from procfs import cli

class ProcFSHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        obj = Proc()
        path = self.path[1:]

        try:
            self.send_response(200, cli.find(path, False))
        except DoesNotExist as e:
            self.send_response(404, "path %s does not exist" % e)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bind', help='bind to address', type=str, default='0.0.0.0')
    parser.add_argument('-p', '--port', help='port to bind to', type=int, default=8080)
    args = parser.parse_args()

    server = ThreadedHTTPServer((args.bind, args.port), ProcFSHandler)
    print 'Starting server on %s:%d - use <Ctrl-C> to stop' % (server.server_address)
    server.serve_forever()
