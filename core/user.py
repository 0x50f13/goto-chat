from hashlib import sha512

from .config import DEFAULT_ENCODING


class User:
    def __init__(self, name: str, passwd: str):
        self.username = name
        self.passwd = passwd
        self.hsh = sha512(passwd + name)
        self.online = False

    def encode(self):
        return bytes(self.username + self.hsh, DEFAULT_ENCODING)
