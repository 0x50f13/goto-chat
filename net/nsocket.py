import socket
import threading
import uuid

from core.config import APP_PORT, MAX_PACKET_SIZE
from net import logger, TooLongPacket
from .util import get_broadcast, chunks, int42bytes





def broadcast(message):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.bind(("", APP_PORT))
    server.sendto(message, (get_broadcast(), APP_PORT))
    server.close()


def udp_send(message, ip, port):
    logger.debug("Sending %s to %s:%d" % (message, ip, port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(message, (ip, port))
    sock.close()


def _udp_send(prefix: bytes, data: bytes, ip: str, port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = chunks(data, MAX_PACKET_SIZE)
    for chunk in data:
        sock.sendto(prefix + chunk, (ip, port))
    logger.debug("Exit:_udp_send")
    sock.close()


def async_udp_send(prefix, data, ip, port):
    logger.info("Running async task on udp send")
    t = threading.Thread(target=_udp_send, args=(prefix, data, ip, port), daemon=True)
    t.start()
