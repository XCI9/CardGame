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
    card_evaluate = Signal(list[Hand])
    update_table = Signal(Hand)
    init_card = Signal(list)
    your_turn = Signal(bool)
    gameover = Signal(str)
    change_turn = Signal(str)
    response_playable = Signal(list)
    update_cards_count = Signal(list)
    update_players = Signal(list, int)
    connection_lose = Signal()

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
                case Package.PrevHand():   self.update_table.emit(package.hand)
                case Package.InitCard():   self.init_card.emit(package.cards)
                case Package.GameOver():   self.gameover.emit(package.winner)
                case Package.YourTurn():   self.your_turn.emit(package.force)
                case Package.ResValid():   self.response_playable.emit(package.replies)
                case Package.ChangeTurn(): self.change_turn.emit(package.name)
                case Package.GameOver():   self.gameover.emit(package.winner)
                case Package.CardLeft():   self.update_cards_count.emit(package.cards_count)
                case Package.GetPlayer():  self.update_players.emit(package.players, package.full_count)
                case _:                    raise NotImplementedError
        self.logger.log('disconnect', self.socket, '')
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.connection_lose.emit()
