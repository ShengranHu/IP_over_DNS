import threading

from dnslib import *
from socket import *
import time

from dns_client import DNS_client
from utils import *


POLL_FLAG   = 'P'.encode()
CONTI_FLAG = 'C'.encode()
END_FLAG   = 'E'.encode()

class DNS_reciever():
    def __init__(self, dns_upstream='120.78.166.34'):
        super().__init__()
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
        self.upstream = (dns_upstream, 53)

        self.dns_client_addr = ('0.0.0.0', 12000)

    def poll(self):
        clientSocket = self.clientSocket
        upstream     = self.upstream

        req = DNSRecord()
        _qname = DNSLabel((POLL_FLAG, ran_generate(32), 'group-38'.encode(), 'cs305'.encode(), 'fun'.encode()))
        q = DNSQuestion(qname=_qname, qtype=QTYPE.TXT)
        req.add_question(q)
        clientSocket.sendto(req.pack(), upstream)
        #print(req)

    def recv(self):
        clientSocket = self.clientSocket

        recv_bytes = clientSocket.recv(1024)
        ans = DNSRecord.parse(recv_bytes)
        # print(ans)
        flag, data = None, None
        if ans.rr:
            for answer in ans.rr:
                print('recv: ', answer)
                if type(answer.rdata) != TXT:
                    continue
                flag, data = answer.rdata.data
                data = str2bytes(data)
                # print(data)
                # print(flag)
                #print(flag, data)

        #clientSocket.sendto(SendBackdata, self.dns_client_addr)
        return flag, data

    def fileno(self):
        return self.clientSocket.fileno()

    def poll_thread(self, poll_freq = 0.1):
        start_time = time.time()
        SendBackdata = bytes()
        while(True):
            self.poll()
            flag, data = self.recv()
            if data:
                SendBackdata += data
                #print(flag, data)
            if flag == END_FLAG:
                self.clientSocket.sendto(SendBackdata, self.dns_client_addr)
                #print(SendBackdata)
                SendBackdata = bytes()
            time.sleep(poll_freq)


if __name__ == '__main__':
    dns_reciever = DNS_reciever()
    poll_thread = threading.Thread(target=dns_reciever.poll_thread)
    poll_thread.start()

