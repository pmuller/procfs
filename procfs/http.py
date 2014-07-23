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

class ProcFSHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        obj = Proc()
        path = self.path[1:]
        failed = -1

        for (k, v) in enumerate(path.split('/')):
            try:
                obj = obj.__getitem__(v)
            except (DoesNotExist, AttributeError) as e:
                failed = k
                break

        if callable(obj):
            obj = obj()

        if failed != -1:
            for (k, v) in enumerate(path.split('/')):
                if k < failed:
                    continue
                try:
                    obj = obj.__getattr__(v)
                except (KeyError, DoesNotExist, AttributeError) as e:
                    try:
                        obj = obj.__getattr__(int(v))
                    except (KeyError, ValueError, DoesNotExist, AttributeError) as e:
                        self.send_error(404, "no such path")
                        return

        if isinstance(obj, ProcDirectory):
            keys = []
            for key in obj.__dir__():
                keys.append(key)
            obj = keys

        self.send_response(200, json.dumps(obj))

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
