import socket
import threading

from core.config import APP_PORT,DEFAULT_ENCODING,MAX_PACKET_SIZE
from .util import get_broadcast,chunks
from net import logger,TooLongPacket


def broadcast(message):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.bind(("", APP_PORT))
    server.sendto(message,(get_broadcast(), APP_PORT))
    server.close()

def udp_send(message,ip,port):
    if len(message)>MAX_PACKET_SIZE:
        raise TooLongPacket("Packet size is more than MAX_PACKET_SIZE,use async_udp_send")
    logger.debug("Sending %s to %s:%d"%(message,ip,port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(message, (ip, port))
    sock.close()

def _udp_send(prefix:bytes,data:bytes,ip: str,port: input()):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data=chunks(data,MAX_PACKET_SIZE)
    for chunk in data:
        sock.sendto(prefix+chunk,(ip,port))
    sock.close()
def async_udp_send(data,ip,port):
    t=threading.Thread(target=_udp_send,args=(data,ip,port),daemon=True)
    t.start()
