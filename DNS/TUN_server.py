import sys
import optparse
import socket
import select
import errno
import pytun

from dns_server import DNS_server

class TunnelServer(object):

    def __init__(self, taddr, tdstaddr, tmask, tmtu, laddr, lport, raddr, rport):
        self._tun = pytun.TunTapDevice(flags=pytun.IFF_TUN|pytun.IFF_NO_PI)
        self._tun.addr = taddr
        self._tun.dstaddr = tdstaddr
        self._tun.netmask = tmask
        self._tun.mtu = tmtu
        self._tun.persist(True)
        self._tun.up()

        self._dns_server = DNS_server()

    def run(self):
        mtu = self._tun.mtu
        r = [self._tun, self._dns_server]; w = []; x = []
        to_tun = ''
        to_sock = ''
        while True:
            try:
                r, w, x = select.select(r, w, x)
                if self._tun in r:
                    to_sock = self._tun.read(mtu)
                if self._dns_server in r:
                    to_tun = self._dns_server.recv_data()
                    if to_tun:
                        print('recv',to_tun)
                    # if addr[0] != self._raddr or addr[1] != self._rport:
                    #     to_tun = '' # drop packet
                if self._tun in w:
                    if to_tun:
                        self._tun.write(to_tun)
                    to_tun = ''
                if self._dns_server in w:
                    print('send: ',to_sock)
                    self._dns_server.sendto(to_sock)
                    to_sock = ''
                r = []; w = []
                if to_tun:
                    w.append(self._tun)
                else:
                    r.append(self._dns_server)
                if to_sock:
                    w.append(self._dns_server)
                else:
                    r.append(self._tun)
            except (select.error, socket.error, pytun.Error) as e:
                # if e[0] == errno.EINTR:
                #     continue
                print(e)
                to_tun = ''
                continue

def main():
    parser = optparse.OptionParser()
    parser.add_option('--tun-addr', dest='taddr', default='10.10.10.2',
            help='set tunnel local address')
    parser.add_option('--tun-dstaddr', dest='tdstaddr', default='10.10.10.1',
            help='set tunnel destination address')
    parser.add_option('--tun-netmask', default='255.255.255.0',dest='tmask',
            help='set tunnel netmask')
    parser.add_option('--tun-mtu', type='int', default=150,dest='tmtu',
            help='set tunnel MTU')
    parser.add_option('--local-addr', default='0.0.0.0', dest='laddr',
            help='set local address [%default]')
    parser.add_option('--local-port', type='int', default=8888, dest='lport',
            help='set local port [%default]')
    parser.add_option('--remote-addr', dest='raddr', default='118.31.12.36',
            help='set remote address')
    parser.add_option('--remote-port', type='int', dest='rport', default=8888,
            help='set remote port')
    opt, args = parser.parse_args()
    if not (opt.taddr and opt.tdstaddr and opt.raddr and opt.rport):
        parser.print_help()
        return 1
    try:
        server = TunnelServer(opt.taddr, opt.tdstaddr, opt.tmask, opt.tmtu,
                opt.laddr, opt.lport, opt.raddr, opt.rport)
    except (pytun.Error, socket.error) as e:
        print (e)
        return 1
    server.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())