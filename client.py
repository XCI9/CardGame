import socket
from utilities import *
import pickle
from package import Package
from PySide6.QtCore import Qt, Signal, QThread
from logger import ConnectionLogger
import struct

HOST = "127.0.0.1"
PORT = 8888

class ClientHandler(QThread):
    gameover = Signal(str)
    update_players = Signal(list, int)
    connection_lose = Signal()
    sync_game = Signal(TableClassic, int)
    others_play_hand = Signal(Hand, int)

    def __init__(self, socket: socket.socket, logger: ConnectionLogger):
        super().__init__()
        self.socket = socket
        self.logger = logger

    def run(self):
        while self.socket.fileno() != -1:
            header = self.socket.recv(4)  # Read the 4-byte header
            if not header:
                break
            length = struct.unpack("!I", header)[0]  # Unpack the message length from network byte order
            data = self.socket.recv(length)
            if not data:
                break
            package = pickle.loads(data)
            self.logger.log('recv', self.socket, str(package))

            match package:
                case Package.GameOver():   self.gameover.emit(package.winner)
                case Package.GetPlayer():  self.update_players.emit(package.players, package.full_count)
                case Package.SyncGame():   self.sync_game.emit(package.table, package.id)
                case Package.PlayCard():   self.others_play_hand.emit(package.hand, package.id)
                case _:                    raise NotImplementedError
        self.logger.log('disconnect', self.socket, '')
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.connection_lose.emit()
