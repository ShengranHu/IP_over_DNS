from dnslib import *
from socket import *
import time
# please pip install dnslib!!!

class DNS_server():

    def __init__(self, upstream_address='120.78.166.34', upstream_port=53):
        # default upstream DNS server is ns2.sustech.edu.cn
        # use post 53 for DNS server
        self.serverPort    = 53
        self.upstream      = (upstream_address, upstream_port)
        self.cache         = {}
        self.cache_ttl     = {}

    def send_recv_upstream(self, request_bytes):
        # send DNS request to upstream, and receive response
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.sendto(request_bytes, self.upstream)
        response_byte, server_address = client_socket.recvfrom(2048)
        client_socket.close()
        return response_byte

    def add_ans(self, ans, ans_tuple):
        # add each fields into reply
        for rr in ans_tuple[0]:
            ans.add_answer(rr)
        for auth in ans_tuple[1]:
            ans.add_auth(auth)
        for ar in ans_tuple[2]:
            ans.add_ar(ar)

    def run(self):
        cache = self.cache
        cache_ttl = self.cache_ttl
        serverPort = self.serverPort
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind(('', serverPort))
        print("DNS server is ready")
        start_time = time.time()
        while True: # start server
            request_bytes, clientAddress = serverSocket.recvfrom(4096)
            # use dnslib.DNSRecord to handle request in bytes
            req = DNSRecord.parse(request_bytes)
            # construct skeleton reply packet
            ans = req.reply()
            for question in req.questions:
                request_flag = False
                # check each question in request, typically 1
                qname  = question.qname
                qtype  = question.qtype
                qclass = question.qclass
                q_tuple = (qname, qtype, qclass)
                # get fields in question field
                if q_tuple in cache:
                    #if there is record in cache
                    ans_tuple = cache[q_tuple]
                    # only add answer
                    # detect the cache whether up to date
                    add_flag = True
                    # for rr in answer, in one of them out of date, the whole rr will be dropped
                    for rr in ans_tuple[0]:
                        cache_time = cache_ttl[q_tuple]
                        if time.time() - cache_time > rr.ttl:
                            add_flag = False
                            request_flag = True
                            break
                    if add_flag:
                        for rr in ans_tuple[0]:
                            ans.add_answer(rr)
                else:
                    request_flag = True
                if request_flag:
                    #if no record cached, send upstream
                    response_byte = self.send_recv_upstream(request_bytes)
                    # handle response_byte
                    res = DNSRecord.parse(response_byte)
                    ans_tuple = (res.rr, res.auth, res.ar)
                    #cache response
                    cache[q_tuple] = ans_tuple
                    # record the time when cache
                    cache_ttl[q_tuple] = time.time()
                    # add each field to our response to client
                    self.add_ans(ans, ans_tuple)
            # flush cache every 1 hour
            if time.time() - start_time >= 3600:
                cache.clear()
                start_time = time.time()
            serverSocket.sendto(ans.pack(), clientAddress)


if __name__ == '__main__':
    DNS_server().run()
