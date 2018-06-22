import logging
import socket

from core.config import LOGFORMAT, APP_PORT, MAX_PACKET_SIZE

log_formatter = logging.Formatter(LOGFORMAT)
logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)


class UDPListener:
    def __init__(self, ip="0.0.0.0", port=APP_PORT):
        self.ip = ip
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run_once(self, timeout=1.0, data_size=16):
        logger.info("Listening for any message on %s:%d" % (self.ip, self.port))
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.ip, self.port))
        self.s.settimeout(timeout)
        try:
            data = self.s.recvfrom(data_size)
        except socket.timeout:
            logger.warning("recvfrom operation timed out")
            return None
        return data

    def reset(self):
        self.s.close()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def set_data_handler(self,handler):
        '''handler:fun<-args:data'''
        self.data_handler=handler

    def run(self):
        logger.info("Setting up on %s:%d"%(self.ip, self.port))
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.ip, self.port))
        assert hasattr(self,"data_handler")
        while True:
            data=self.s.recvfrom(MAX_PACKET_SIZE)
            self.data_handler(data)