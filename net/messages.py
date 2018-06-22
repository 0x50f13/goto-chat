import uuid

from core.config import MAX_PACKET_SIZE, DEFAULT_ENCODING
from net import logger
from .nsocket import udp_send
from .util import ip2bytes, local_ip, int42bytes, chunks

MESSAGE_CONN_ACCEPTED = b'\6\1'  # response if connection was accepted
MESSAGE_LOGIN = b'\6\2'  # Login to the network request
MESSAGE_AUTH = b'\6\4'
MESSAGE_AUTH_FAILURE = b'\6\3'
MESSAGE_AUTH_OK = b'\6\5'
MESSAGE_DATA_SEND = b'\6\7'
MESSAGE_DATA_LONG = b'\6\10'
MESSAGE_SYNC = b'\6\11'
MESSAGE_SYNC_RESP = b'\6\12'


class Message:
    def __init__(self, data: bytes, src: str):

        self.data = data
        self.data_len = len(data)
        self.chunk_size = MAX_PACKET_SIZE
        self.uuid = str(uuid.uuid4())
        self.chunks = []
        self.chunks = [chunk for chunk in chunks(self.data, self.chunk_size)]

    @staticmethod
    def unpack_packet(x: bytes):
        return x.split(b"\1\1\1\1\1")

    @staticmethod
    def is_vready(vec):
        return b"\4" not in vec

    def generate_header(self, packet_id):  ##TODO:assert max int 4-bytes

        header = int42bytes(len(self.chunks)) + b"\1\1\1\1\1" + int42bytes(packet_id) + b"\1\1\1\1\1" + bytes(
            self.uuid, DEFAULT_ENCODING) + b"\1\1\1\1\1"
        return header

    def packets(self):
        packets = []
        assert len(self.chunks[0]) <= len(self.data)

        for i in range(len(self.chunks)):
            packet = self.generate_header(i + 1) + bytes(self.chunks[i])
            yield packet

    def add_packet(self, data: bytes):
        chunks_count, packet_id, _uuid, data = data.split(b"\1\1\1\1\1")
        if not self.chunks:  # First packet
            self.chunks = [b"\4"] * chunks_count
            self.uuid = _uuid
            self.chunks[packet_id] = data
        else:
            if self.uuid != _uuid:
                logger.warning("UUID mismatch while receiving packets.Ignored.")
                return
            else:
                self.chunks[packet_id] = data

    def chunks2data(self):
        self.data = ""
        for chunk in self.chunks:
            self.data += chunk

    def is_ready(self):
        self.is_vready(self.chunks)


class MessageController:  ##TODO:DDoS memory fluid protection
    def __init__(self):
        self.messages = dict()

    def receive(self, packet: bytes, src: str):
        _, _, _uuid, _ = Message.unpack_packet(packet)
        if _uuid not in self.messages:
            self.start_recieve(packet,src)
            return
        self.messages[_uuid].add_packet(packet)

    def start_recieve(self, packet: bytes, src: str):
        _, _, _uuid, _ = Message.unpack_packet(packet)
        logger.info("Starting receiving data for uuid:" + _uuid)
        if _uuid in self.messages:
            self.receive(packet,src)
            return
        self.messages.update({_uuid: Message(packet,src)})

    def get_unread(self):
        unread = []
        for key in self.messages:
            if self.messages[key].is_ready():
                unread.append(self.messages[key])
                self.messages.pop(key)
        return unread


messagectl = MessageController()


def gen_wait_message():
    return MESSAGE_LOGIN + ip2bytes(local_ip())


def decode_message(msg):
    cmd = msg[:2]
    data = msg[2:]
    return cmd, data


def send_message(purpose, payload: bytes, ip: str, port: int):
    data = purpose + payload
    udp_send(data, ip, port)
