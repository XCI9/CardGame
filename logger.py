import logging
from typing import Literal
import socket

class ConnectionLogger:
    def __init__(self, name:str):
        self.logger = logging.getLogger(name=name)
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(name)s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log(self, type:Literal['recv','send', 'connect', 'disconnect'], target_socket: socket.socket, msg: str):
        match type:
            case 'recv':       status = '<<<'
            case 'send':       status = '>>>'
            case 'connect':    status = '<->'
            case 'disconnect': status = '-x-'
        ip, port = target_socket.getpeername()
        
        self.logger.info(f'{status} {ip:>16}:{port:<5}]{msg}')
        