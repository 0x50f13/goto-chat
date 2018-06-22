import socket

from core.config import APP_PORT,DEFAULT_ENCODING
from .util import get_broadcast


def broadcast(message):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.bind(("", APP_PORT))
    server.sendto(message,(get_broadcast(), APP_PORT))
    server.close()

def udp_send(message,ip,port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(message, (ip, port))
    sock.close()