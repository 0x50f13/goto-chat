from hashlib import sha512

from core import logger
from net.messages import gen_wait_message
from net.nsocket import broadcast
from .config import BROADCAST_WAIT_TIMEOUT
from net import UDPListener


class App:
    def __init__(self):
        self.username = "<NONE>"
        self.userpass = "<NONE>"
        self.listener=UDPListener()

    def set_user(self, user, _pass):
        self.username = user
        self.userpass = _pass
        self._hash = sha512(user + _pass)
        logger.info("Setted user to %s" % (self.username))

    def connect(self):
        logger.info("Starting broadcast and waiting to response...")
        broadcast(gen_wait_message(), timeout=BROADCAST_WAIT_TIMEOUT)
        if self.listener.run_once(timeout=BROADCAST_WAIT_TIMEOUT) == None:
            logger.error("Failed to find any other nodes")
        logger.info("Starting listener for broadcasts")


def main():
    app = App()
    app.connect()
