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
        self.auth_dict=dict()

    def set_user(self, user:User):
        self.user=user
        logger.info("Setted user to %s" % (self.user))

    def data_handler(self, data):
        _data, addr = data
        cmd, data = decode_message(_data)
        logger.debug("Received:%s" % str(_data))
        if cmd == MESSAGE_LOGIN:##Establsihing connctions is here
            logger.info("Received login req from " + str(addr))
            udp_send(MESSAGE_CONN_ACCEPTED, addr[0], addr[1])
            network.known_nodes.append(addr)
        if cmd == MESSAGE_CONN_ACCEPTED:
            logger.info("Adding %s to known nodes list"%str(addr))
            network.known_nodes.append(addr)
        if cmd == MESSAGE_AUTH:#Authentication procedure
            user,_=data.split("\12\12\12\12\12")
            _user=User("","")
            _user.decode(user)
            if _user.username in network.users:
                udp_send(MESSAGE_AUTH_FAILURE,addr[0],APP_PORT)
            else:
                udp_send(MESSAGE_AUTH_OK,addr[0],APP_PORT)
                network.users.update({_user.username:_user})
            for node in network.known_nodes:
                if node not in self.auth_dict:
                    return
            del self.auth_dict
            self.is_authenticated=True

        if cmd == MESSAGE_AUTH_FAILURE and not self.is_authenticated:
            raise SystemError("Authentication failed!")

        if cmd == MESSAGE_AUTH_OK and not self.is_authenticated:
            self.auth_dict.update({addr[0]:True})


    def auth(self,user: User):
        logger.info("Starting authentication...")
        payload=user.encode()
        payload+="\12\12\12\12\12"
        payload+=ip2bytes(local_ip())##NEEDED IF AUTHENTICATION'LL REQUIRE PASSWORD,SO EACH NODE COULD SEND A CALLBACK
        for node in network.known_nodes:
            logger.debug("Sending auth request to node:"+str(node))
            udp_send(MESSAGE_AUTH+payload,node[0],APP_PORT)
        logger.info("Done sending auth requests to other nodes")

    def connect(self):
        logger.info("Starting broadcast and waiting to response...")
        broadcast(gen_wait_message())
        logger.info("Starting listener for broadcasts")
        self.listener.reset()
        self.listener.set_data_handler(self.data_handler)
        self.listener_thread = threading.Thread(target=self.listener.run,daemon=True)
        self.listener_thread.run()



def main():
    app = App()
    app.connect()
    me=User("d3ad","1712")
    app.auth(me)

