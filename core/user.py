from hashlib import sha512

from .config import DEFAULT_ENCODING


class User:
    def __init__(self, name: str, passwd: str):
        self.username = name
        self.passwd = passwd
        self.hsh = sha512((passwd + name).encode(DEFAULT_ENCODING)).hexdigest()
        self.online = False
        self.node_ip = "0.0.0.0"

    def encode(self):
        return bytes("\2" + self.username + "\3\2" + self.hsh + "\3", DEFAULT_ENCODING)

    def decode(self, dbytes: bytes):
        s = str(dbytes, DEFAULT_ENCODING)
        username, hsh = s.split("\3\2")
        username = username.replace("\2", "")
        hsh = hsh.replace("\3", "")
        self.username = username
        self.hsh = hsh

    def check(self):
        if sha512(self.passwd + self.username) == self.hsh:
            return True
        else:
            return False

    def __repr__(self):
        return "<User '%s'>" % self.username

    def __str__(self):
        return self.username
