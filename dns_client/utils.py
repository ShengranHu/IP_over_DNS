import base64
import time
import random

hex_char = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']

def bytes2str(data : bytes) -> bytes:
    return base64.urlsafe_b64encode(data)

def str2bytes(string : bytes) -> bytes:
    return base64.urlsafe_b64decode(string)

def ran_generate(length) -> bytes:

    assert length % 2 == 0
    rand = bytes()
    for _ in range(length):
        rand += hex_char[random.randint(0, 15)].encode()

    return rand

if __name__ == '__main__':
    print(ran_generate(32))