# -*- encoding: utf-8 -*-
import os
import sys
import signal

if os.path.dirname(__file__) != '/usr/lib/python2.7/dist-packages/globaleaks/workers':
    sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from twisted.internet import reactor
from twisted.internet.defer import DeferredList

from globaleaks.workers.process import Process
from globaleaks.utils.sock import listen_tls_on_sock
from globaleaks.utils.sni import SNIMap
from globaleaks.utils.tls import TLSServerContextFactory, ChainValidator
from globaleaks.utils.httpsproxy import HTTPStreamFactory

class HTTPSProcess(Process):
    name = 'gl-https-proxy'
    ports = []

    def __init__(self, *args, **kwargs):
        super(HTTPSProcess, self).__init__(*args, **kwargs)
        self.log('HTTPSProcess started')

        proxy_url = 'http://' + self.cfg['proxy_ip'] + ':' + str(self.cfg['proxy_port'])

        http_proxy_factory = HTTPStreamFactory(proxy_url, self.log)

        cv = ChainValidator()
        ok, err = cv.validate(self.cfg, must_be_disabled=False, check_expiration=False)
        if not ok or not err is None:
            raise err

        snimap = SNIMap({
            'DEFAULT': TLSServerContextFactory(self.cfg['ssl_key'],
                                               self.cfg['ssl_cert'],
                                               self.cfg['ssl_intermediate'],
                                               self.cfg['ssl_dh'])
        })

        socket_fds = self.cfg['tls_socket_fds']

        for socket_fd in socket_fds:
            self.log("Opening socket: %d : %s" % (socket_fd, os.fstat(socket_fd)))

            port = listen_tls_on_sock(reactor,
                                      fd=socket_fd,
                                      contextFactory=snimap,
                                      factory=http_proxy_factory)

            self.ports.append(port)
            self.log("HTTPS proxy listening on %s" % port)

    def shutdown(self):
        self.log("HTTPSProcess.log shutdown")

        dl = []
        for port in self.ports:
            self.log("HTTPProcess stopping on %s" % port)
            dl.append(port.loseConnection())
        self.log("Waiting for %s" % dl)
        return DeferredList(dl)


if __name__ == '__main__':
    h = HTTPSProcess()
    h.log("HTTPSProcess.log main")

    def stop_handler(signum, frame):
        h.log('Signal handler called with signal: %d' % signum)
        h.shutdown().addBoth(reactor.stop)

    signal.signal(signal.SIGUSR1, stop_handler)

    h.start()
