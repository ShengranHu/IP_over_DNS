from dnslib import *
from socket import *
import time
from utils import *
import dnslib

CONTI_FLAG = 'C'.encode()
END_FLAG   = 'E'.encode()
POLL_FLAG   = 'P'.encode()

class DNS_server():

    def __init__(self):
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind(('0.0.0.0', 53))
        self.cache        = []

    def recvfrom(self):
        serverSocket = self.serverSocket

        request_bytes, address = serverSocket.recvfrom(1024)
        req = DNSRecord.parse(request_bytes)
        question, = req.questions
        qname = question.qname
        #print(qname)
        flag = None
        data = bytes()

        for index, field in enumerate(qname.label):
            if index == 0:
                flag = field
            elif field != b'group-38':
                data += field
            else:
                break

        ans = req.reply()
        serverSocket.sendto(ans.pack(), address)
        return str2bytes(data), flag

    def recv_data(self):
        recv = bytes()
        missTimeConti = 0
        while(True):
            if self.cache:
                data, flag = self.cache.pop()
                recv += data
                if flag == END_FLAG:
                    break

            data, flag = self.recvfrom()

            if flag == POLL_FLAG:
                break

            if flag == END_FLAG or flag == CONTI_FLAG:
                recv += data
                missTimeConti = 0

            if flag == END_FLAG:
                break


        return recv

    def sendto(self, data2send):
        MAX_LENGTH = 248

        data       = bytes2str(data2send)
        total_len = len(data)
        start = 0
        end = 0
        while (total_len - start > MAX_LENGTH):
            end = start + MAX_LENGTH
            self.send_single_pkt(data[start:end], CONTI_FLAG)
            #if start == 0:
                #time.sleep(0.01)
            start = end

        #time.sleep(0.01)
        self.send_single_pkt(data[end:], END_FLAG)


    def send_single_pkt(self, data2send, FLAG):

        serverSocket = self.serverSocket

        request_bytes, address = serverSocket.recvfrom(1024)
        req = DNSRecord.parse(request_bytes)
        question, = req.questions
        qname = question.qname
        #print(qname)
        flag = qname.label[0]
        data = qname.label[1]
        ans = req.reply()
        if flag != POLL_FLAG:
            self.cache.append((str2bytes(data), flag))

        rr = RR(qname, QTYPE.TXT, ttl=0, rdata=TXT((FLAG , data2send)))
        ans.add_answer(rr)

        #print(ans)
        serverSocket.sendto(ans.pack(), address)


    def fileno(self):
        return self.serverSocket.fileno()

if __name__ == '__main__':
    server = DNS_server()
    while True:
        print(server.recv_data())