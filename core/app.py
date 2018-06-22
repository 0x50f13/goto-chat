import threading
from hashlib import sha512

from core import logger
from net import UDPListener, network
from net.messages import *
from net.nsocket import broadcast, udp_send
from .config import BROADCAST_WAIT_TIMEOUT, MAX_NODE_COUNT, APP_PORT
from .user import User
from net.util import local_ip
from net.messages import send_message
##TODO:String length checking e.g. names and messages
class UIController:
    def on_message(self, username, message, data):
        pass

    def on_file(self, username, file_hash, file_id):
        pass

ui = UIController()


class App:
    def __init__(self):
        self.listener = UDPListener()
        self.is_authenticated=False

    def set_user(self, user:User):
        self.user=user
        logger.info("Setted user to %s" % (self.user))

    def data_handler(self, data):
        _data, addr = data
        cmd, data = decode_message(_data)
        logger.debug("Received:%s" % str(_data))
        if cmd == MESSAGE_LOGIN:
            logger.info("Received login req from " + str(addr))
            udp_send(MESSAGE_CONN_ACCEPTED, addr[0], addr[1])
            network.known_nodes.append(addr)
        if cmd == MESSAGE_CONN_ACCEPTED:
            logger.info("Adding %s to known nodes list"%str(addr))
            network.known_nodes.append(addr)


    def auth(self,user: User):
        payload=user.encode()
        payload+="\12\12\12\12\12"
        payload+=ip2bytes(local_ip())##NEEDED IF AUTHENTICATION'LL REQUIRE PASSWORD,SO EACH NODE COULD SEND A CALLBACK
        for node in network.known_nodes:
            udp_send(MESSSAGE_AUTH+payload,node[0],node[1])
        logger.info("Done sending auth requests to other nodes")
    def connect(self):
        logger.info("Starting broadcast and waiting to response...")
        broadcast(gen_wait_message())
        logger.info("Starting listener for broadcasts")
        self.listener.reset()
        self.listener.set_data_handler(self.data_handler)
        self.listener_thread = threading.Thread(target=self.listener.run)
        self.listener_thread.run()



def main():
    app = App()
    app.connect()
