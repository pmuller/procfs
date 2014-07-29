
"""
.. module:: procfs.http
  :synopsis: procfs HTTP interface
  :platform: Unix
.. moduleauthor:: Robert Xu <robxu9@gmail.com>

"""
import argparse

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

from procfs import Proc
from procfs.exceptions import DoesNotExist
from procfs import cli

class ProcFSHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        obj = Proc()
        path = self.path[1:]

        try:
            response = cli.find(path, False)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response)
        except DoesNotExist as e:
            self.send_error(404, "path %s does not exist" % e)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bind', help='bind to address', type=str, default='0.0.0.0')
    parser.add_argument('-p', '--port', help='port to bind to', type=int, default=8080)
    args = parser.parse_args()

    server = ThreadedHTTPServer((args.bind, args.port), ProcFSHandler)
    print 'Starting server on %s:%d - use <Ctrl-C> to stop' % (server.server_address)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
