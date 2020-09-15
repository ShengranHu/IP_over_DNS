from dnslib import *
from socket import *

from utils import *

CONTI_FLAG = 'C'.encode()
END_FLAG   = 'E'.encode()


MAX_LENGTH = 240
SPLT_LENGTH = 60

class DNS_client():

    def __init__(self, dns_upstream='120.78.166.34'):
        super().__init__()
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
        self.upstream = (dns_upstream, 53)
        self.clientSocket.bind(('0.0.0.0', 12000))

    def sendto(self, data):
        clientSocket = self.clientSocket
        upstream     = self.upstream
        #print('bytes send: ', data)
        data         = bytes2str(data)

       # print('str send: ', data.decode())

        total_len = len(data)
        start = 0
        end = 0
        req = DNSRecord()
        label_byte = bytes()
        label_byte += END_FLAG + b'.'
        while total_len - start > SPLT_LENGTH:
            end = start + SPLT_LENGTH
            label_byte += data[start:end] + b'.'
            start = end

        label_byte += data[end:total_len] + b'.'
        label_byte += b'group-38.cs305.fun'

        _qname = DNSLabel(label_byte)
        q = DNSQuestion(qname=_qname, qtype=QTYPE.TXT)

        print('send: ', q)
        req.add_question(q)

        clientSocket.sendto(req.pack(), upstream)
        #clientSocket.recv(1024)
        #print(req)
        #print(DNSRecord.parse())

    def recv(self):
        recv, addr = self.clientSocket.recvfrom(1024)
        if addr[1] == 53:
            recv = ''
        return recv


    def fileno(self):
        return self.clientSocket.fileno()



if __name__ == '__main__':
    client = DNS_client()
    client.sendto(ran_generate(150))

