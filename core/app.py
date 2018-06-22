from hashlib import sha512

from core import logger
from net.messages import gen_wait_message
from net.nsocket import broadcast
from .config import BROADCAST_WAIT_TIMEOUT
from net import UDPListener
import threading


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

    def data_handler(self,data):
        print(str(data))
    def connect(self):
        logger.info("Starting broadcast and waiting to response...")
        broadcast(gen_wait_message())
        if self.listener.run_once(timeout=BROADCAST_WAIT_TIMEOUT) == None:
            logger.error("Failed to find any other nodes")
        logger.info("Starting listener for broadcasts")
        self.listener.reset()
        self.listener.set_data_handler(self.data_handler)
        self.listener_thread=threading.Thread(target=self.listener.run,daemon=True)
        self.listener_thread.run()

def main():
    app = App()
    app.connect()
