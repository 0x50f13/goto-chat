from core.config import NET_DATA, DEFAULT_ENCODING
from ipaddress import IPv4Network

import socket
import struct

def get_broadcast():
    net=IPv4Network(NET_DATA,False)
    return str(net.broadcast_address)

def ip2bytes(ip: str):
    _ip=struct.unpack('BBBB', socket.inet_aton(ip))
    s=""
    for x in _ip:
        s+=chr(x)
    return bytes(s,DEFAULT_ENCODING)

def local_ip():
    return socket.gethostbyname(socket.gethostname())