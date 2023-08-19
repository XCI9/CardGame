import logging
from typing import Literal
import socket
from PySide6.QtNetwork import QTcpSocket

class ConnectionLogger:
    def __init__(self, name:str):
        self.logger = logging.getLogger(name=name)
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(name)s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log(self, type:Literal['recv','send', 'connect', 'disconnect'], target_socket: socket.socket|QTcpSocket, msg: str):
        match type:
            case 'recv':       status = '<<<'
            case 'send':       status = '>>>'
            case 'connect':    status = '<->'
            case 'disconnect': status = '-x-'
        if isinstance(target_socket, socket.socket):
            ip, port = target_socket.getpeername()
        elif isinstance(target_socket, QTcpSocket):
            ip = target_socket.peerAddress().toString()
            port = target_socket.peerPort()
        
        self.logger.info(f'{status} {ip:>16}:{port:<5}]{msg}')
        