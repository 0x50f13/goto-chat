from .util import ip2bytes, local_ip

MESSAGE_CONN_ACCEPTED = b'\6\1'
MESSAGE_LOGIN = b'\6\2'
MESSAGE_REQUEST_NET = b'\6\3'
MESSAGE_AUTH=b'\6\4'
MESSAGE_BEACON=b'\6\5'


def gen_wait_message():
    return MESSAGE_LOGIN + ip2bytes(local_ip())


def decode_message(msg):
    cmd = msg[:2]
    data = msg[2:]
    return cmd,data
