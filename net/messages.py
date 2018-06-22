from .util import ip2bytes, local_ip

MESSAGE_WAIT_ACCEPT = b'\6\1'
MESSAGE_ACCEPT = b'\6\2'


def gen_wait_message():
    return MESSAGE_ACCEPT + ip2bytes(local_ip())
