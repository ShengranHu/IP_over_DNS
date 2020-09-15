import random
import base64
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
    data = bytes.fromhex(
        '9cb6d0215a97407183ab300386dd6c00000000203aff20010da8201d11010000000000000001ff0200000000000000000001ff1e7b21870085b90000000020010da8201d110316f8adbc871e7b210101407183ab3003')
    print(bytes2str(data))
    print(type(bytes2str(data)))
    print(str2bytes(bytes2str(data)))
    print(type(str2bytes(bytes2str(data))))