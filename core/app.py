import threading
from hashlib import sha512

from core import logger
from net import UDPListener, network
from net.messages import *
from net.nsocket import broadcast, udp_send
from .config import BROADCAST_WAIT_TIMEOUT, MAX_NODE_COUNT


class App:
    def __init__(self):
        self.username = "<NONE>"
        self.userpass = "<NONE>"
        self.listener = UDPListener()

    def set_user(self, user, _pass):
        self.username = user
        self.userpass = _pass
        self._hash = sha512(user + _pass)
        logger.info("Setted user to %s" % (self.username))

    def data_handler(self, data):
        _data, addr = data
        cmd, data = decode_message(_data)
        logger.debug("Received:%s" % str(_data))
        if cmd == MESSAGE_LOGIN:
            logger.info("Received login req from " + str(addr))
            if len(network.known_nodes) < MAX_NODE_COUNT:
                logger.info("Accepting login req,sending MESSAGE_ACCEPTED")
                udp_send(MESSAGE_CONN_ACCEPTED, addr[0], addr[1])
                network.known_nodes.append(addr)
        if cmd == MESSAGE_BEACON:
            logger.info("Received beacon from %s"%str(addr))
            network.known_nodes.append(addr)
            logger.info("Connection succesfully established")

    def connect(self):
        logger.info("Starting broadcast and waiting to response...")
        broadcast(gen_wait_message())
        data = self.listener.run_once(timeout=BROADCAST_WAIT_TIMEOUT)
        if data is None:
            logger.error("Failed to find any other nodes")
        else:
            logger.debug("Received data(%s),so adding address to known nodes" % data[0])
            _, addr = data
            cmd, data = decode_message(data[0])
            if cmd == MESSAGE_CONN_ACCEPTED:
                logger.info("Established connection with " + addr[0])
                network.known_nodes.append(addr)
        logger.info("Starting listener for broadcasts")
        self.listener.reset()
        self.listener.set_data_handler(self.data_handler)
        self.listener_thread = threading.Thread(target=self.listener.run)
        self.listener_thread.run()


class UIController:
    def on_message(self, username, message, data):
        pass

    def on_file(self, username, file_hash, file_id):
        pass

ui=UIController()


def main():
    app = App()
    app.connect()
