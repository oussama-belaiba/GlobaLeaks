import sys
from time import sleep

import SocketServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SimpleHTTPServer import test

class SlowHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        sleep(10)
        SimpleHTTPRequestHandler.do_GET(self)

    def end_headers(self):
        SimpleHTTPRequestHandler.end_headers(self)
        self.send_header('Server','kpiQuest')

port = int(sys.argv[1])

httpd = SocketServer.TCPServer(("127.0.0.1", port), SlowHTTPRequestHandler)
print "serving at port", port

import signal, sys
import threading

def SigQuit(_, x):
    print 'shutting down'
    httpd.shutdown()
    httpd.server_close()
    print 'fin'
    sys.exit()

signal.signal(signal.SIGUSR1, SigQuit)

t = threading.Thread(target=httpd.serve_forever)
t.start()

while True:
    pass

print 'never got here'
