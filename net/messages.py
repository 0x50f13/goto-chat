import uuid

from core.config import DEFAULT_ENCODING
from .util import ip2bytes, local_ip
from .nsocket import udp_send
MESSAGE_CONN_ACCEPTED = b'\6\1'  # response if connection was accepted
MESSAGE_LOGIN = b'\6\2'  # Login to the network request
MESSSAGE_AUTH = b'\6\4'


def gen_wait_message():
    return MESSAGE_LOGIN + ip2bytes(local_ip())


def decode_message(msg):
    cmd = msg[:2]
    data = msg[2:]
    return cmd, data

def send_message(purpose,payload: bytes,ip:str,port:int):
    data=purpose+payload
    udp_send(data,ip,port)
