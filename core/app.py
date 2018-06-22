# WARNING:In this code thousands of bugs and holes.Beware!!!
import threading
import time

from core import logger
from net import UDPListener, network
from net.messages import *
from net.nsocket import broadcast, udp_send
from net.util import local_ip
from .config import APP_PORT
from .user import User


##TODO:String length checking e.g. names and messages
class UIController:
    def on_message(self, data):
        print(data)

    def on_file(self, username, file_hash, file_id):
        pass


ui = UIController()


class App:
    def __init__(self):
        self.listener = UDPListener()
        self.is_authenticated = False
        self.auth_dict = dict()

    #        self.end_connect=threading.Event()
    #        self.end_connect.clear()

    def set_user(self, user: User):
        self.user = user
        logger.info("Setted user to %s" % (self.user))

    def data_handler(self, data):
        _data, addr = data
        cmd, data = decode_message(_data)
        logger.debug("Received:%s" % str(_data))
        if cmd == MESSAGE_LOGIN:  ##Establsihing connctions is here
            logger.info("Received login req from " + str(addr))
            udp_send(MESSAGE_CONN_ACCEPTED, addr[0], APP_PORT)
            logger.info("Adding %s to known nodes" % addr[0])
            if addr not in network.known_nodes:
                network.known_nodes.append(addr)
        if cmd == MESSAGE_CONN_ACCEPTED:
            logger.info("Adding %s to known nodes list" % str(addr))
            if addr not in network.known_nodes:
                network.known_nodes.append(addr)
        if cmd == MESSAGE_AUTH:  # Authentication procedure
            user, _ = data.split(b"\17\12\20\17")
            _user = User("", "")
            _user.decode(user)
            if _user.username in network.users:
                udp_send(MESSAGE_AUTH_FAILURE, addr[0], APP_PORT)
            else:
                udp_send(MESSAGE_AUTH_OK, addr[0], APP_PORT)
                network.users.update({_user.username: addr})
            for node in network.known_nodes:
                if node not in self.auth_dict:
                    return
            del self.auth_dict
            self.is_authenticated = True

        if cmd == MESSAGE_AUTH_FAILURE and not self.is_authenticated and addr[0] in network.known_nodes:
            raise SystemError("Authentication failed!")

        if cmd == MESSAGE_AUTH_OK and not self.is_authenticated:
            self.auth_dict.update({addr[0]: True})

        if cmd == MESSAGE_DATA_LONG:
            messagectl.receive(data)

    def send_msg(self, data: bytes):
        msg = Message(data)
        for node in network.known_nodes:
            p4s=msg.packets()
            for pack in p4s:
                logger.info("Sending packet to %s,len=%d"%(node,len(pack)))
                udp_send(pack, node[0], APP_PORT)

    def auth(self, user: User):
        logger.info("Starting authentication...")
        payload = user.encode()
        payload += b"\17\12\20\17"
        payload += ip2bytes(
            local_ip())  ##NEEDED IF AUTHENTICATION'LL REQUIRE PASSWORD,SO EACH NODE COULD SEND A CALLBACK
        for node in network.known_nodes:
            logger.debug("Sending auth request to node:" + str(node))
            udp_send(MESSAGE_AUTH + payload, node[0], APP_PORT)
        logger.info("Done sending auth requests to other nodes")
        network.users.append(user)

    def connect(self):
        logger.info("Starting broadcast and waiting to response...")
        broadcast(gen_wait_message())
        logger.info("Starting listener for broadcasts")
        self.listener.reset()
        self.listener.set_data_handler(self.data_handler)
        self.listener_thread = threading.Thread(target=self.listener.run)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        logger.debug("Exiting App.connect")

    def test(self):
        logger.info("Begin testing")
        s=bytes("3"*10000,"utf-8")
        self.send_msg(s)
    def idle(self):
        while True:
            time.sleep(0.1)


def main():
    app = App()
    app.connect()
    me = User("user", "password")
    time.sleep(1)
    app.auth(me)
    app.test()
    app.idle()


