import socket

from core.config import APP_PORT
from .util import get_broadcast


def broadcast(message, timeout=4.0):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.settimeout(timeout)
    server.bind(("", APP_PORT))
    server.sendto(message,(get_broadcast(), APP_PORT))
    data = server.recvfrom(255)
    server.close()
    return data


