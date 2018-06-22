# WARNING:In this code thousands of bugs and holes.Beware!!!
# WARNING:Spaghetti code hazard!!!
import threading
import time
import sys

from core import logger
from net import UDPListener, network
from net.messages import *
from net.nsocket import broadcast, udp_send
from net.util import local_ip
from .config import APP_PORT
from .user import User
import getpass


##TODO:String length checking e.g. names and messages
class UIController:
    def __init__(self):
        self.app=None
    def on_auth_failure(self):
        print("Failed to authnticate in network :(")
    def on_message_received(self,user,msg):
        sys.stdout.flush()
        print("\r\r")
        sys.stdout.flush()
        print("\033[1m%s\033[0m:%s")
    def updater(self):
        while True:
            unread=messagectl.get_unread()
            for msg in unread:
                print("\033[1m[%s]:\033[0m%s"%(network.users[msg.src],msg.chunks2data()))
            time.sleep(0.5)
    def idle(self):
        while True:
            inp=input("\033[1m[%s]>\033[0m"%str(network.users["127.0.0.1"]))





ui = UIController()


class App:
    def __init__(self):
        self.listener = UDPListener()
        self.is_authenticated = False
        self.auth_dict = dict()
        self.ui=None

    #        self.end_connect=threading.Event()
    #        self.end_connect.clear()
    def set_ui(self,ui):
        ui.app=self
        self.ui=ui

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
            _user.decode(user)#decoding user
            if _user.username in network.users:
                udp_send(MESSAGE_AUTH_FAILURE, addr[0], APP_PORT)
            else:
                udp_send(MESSAGE_AUTH_OK, addr[0], APP_PORT)
                network.users.update({addr[0]:_user})
            for node in network.known_nodes:
                if node not in self.auth_dict:
                    return
            del self.auth_dict
            self.is_authenticated = True

        if cmd == MESSAGE_AUTH_FAILURE and not self.is_authenticated and addr[0] in network.known_nodes:
            self.ui.on_auth_failure()
            sys.exit(-1)

        if cmd == MESSAGE_AUTH_OK and not self.is_authenticated:
            self.auth_dict.update({addr[0]: True})

        if cmd == MESSAGE_DATA_LONG:
            logger.info("Begin receiving long data...")
            messagectl.receive(data,addr[0])

    def send_msg(self, data: bytes):
        msg = Message(data,local_ip())
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
        network.users.update({"127.0.0.1":str(user)})

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

    def test(self):###DELETEME###
        logger.info("Begin testing")
        s=bytes("3"*10000,"utf-8")
        self.send_msg(s)
    def idle(self):
        while True:
            time.sleep(0.1)


def main():
    app = App()
    app.connect()
    logger.info("Seems to be connected")
    login=input("Login:")
    passw=getpass.getpass("Password:")
    app.auth(User(login,passw))
    app.set_ui(ui)
    ui.idle()
