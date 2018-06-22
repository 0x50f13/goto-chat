from hashlib import sha512

from core import logger
from net.messages import *
from net.nsocket import broadcast,udp_send
from .config import BROADCAST_WAIT_TIMEOUT,MAX_NODE_COUNT
from net import UDPListener,network
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
        _data,addr=data
        cmd,data=decode_message(_data)
        if cmd==MESSAGE_LOGIN:
            logger.info("Received login beacon from "+str(addr))
            if len(network.known_nodes)<MAX_NODE_COUNT:
                logger.info("Accepting login beacon,sending MESSAGE_ACCEPTED")
                udp_send(MESSAGE_CONN_ACCEPTED,addr[0],addr[1])
        if cmd==MESSAGE_BEACON:
            network.known_nodes.append(addr)
            logger.info("Established connection:received beacon")

    def connect(self):
        logger.info("Starting broadcast and waiting to response...")
        broadcast(gen_wait_message())
        data= self.listener.run_once(timeout=BROADCAST_WAIT_TIMEOUT)
        if data is None:
            logger.error("Failed to find any other nodes")
        else:
            logger.debug("Received data(%s),so adding address to known nodes"%data[0])
            _,addr=data
            cmd,data=decode_message(data[0])
            if cmd==MESSAGE_CONN_ACCEPTED:
                udp_send(MESSAGE_BEACON,addr[0],addr[1])
                logger.info("Established connection with "+addr[0])
        logger.info("Starting listener for broadcasts")
        self.listener.reset()
        self.listener.set_data_handler(self.data_handler)
        self.listener_thread=threading.Thread(target=self.listener.run)
        self.listener_thread.run()

def main():
    app = App()
    app.connect()
