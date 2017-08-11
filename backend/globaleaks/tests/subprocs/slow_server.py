import sys
from time import sleep

import SocketServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SimpleHTTPServer import test

class SlowHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        sleep(3)
        SimpleHTTPRequestHandler.do_GET(self)

    def end_headers(self):
        SimpleHTTPRequestHandler.end_headers(self)
        self.send_header('Server','kpnQuest')

port = int(sys.argv[1])

httpd = SocketServer.TCPServer(("127.0.0.1", port), SlowHTTPRequestHandler)
print "serving at port", port

httpd.serve_forever()
