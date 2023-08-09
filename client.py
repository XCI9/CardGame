import socket
from game import *
import pickle
from package import Package
from PySide6.QtWidgets import QFileDialog, QTableWidgetItem
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, Signal, Slot, QThread, QWaitCondition, QMutex, QObject

HOST = "127.0.0.1"
PORT = 8888

class NetworkHandler(QThread):
    card_evaluate = Signal(list[Hand])
    update_table = Signal(Hand)
    init_card = Signal(list)
    your_turn = Signal(bool)
    gameover = Signal(str)
    change_turn = Signal(str)
    response_playable = Signal(list)
    update_cards_count = Signal(list)
    update_players = Signal(list)

    def __init__(self, socket: socket.socket):
        super().__init__()
        self.socket = socket

    def run(self):
        while True:
            data = self.socket.recv(1024)
            if not data:
                break
            package = pickle.loads(data)

            match package:
                case Package.PrevHand():
                    prev_hand = package.hand
                    self.update_table.emit(prev_hand)
                case Package.InitCard():
                    cards = package.cards
                    self.init_card.emit(cards)
                case Package.GameOver():
                    winner = package.winner
                    print(f'gameover, winner:{winner}')
                    self.gameover.emit(winner)
                case Package.YourTurn():
                    print('my turn')
                    force = package.force
                    self.your_turn.emit(force)
                case Package.ResValid():
                    replies = package.replies
                    self.response_playable.emit(replies)
                case Package.ChangeTurn():
                    name = package.name
                    self.change_turn.emit(name)
                case Package.GameOver():
                    winner = package.winner
                    self.gameover.emit(winner)
                case Package.CardLeft():
                    cards_count = package.cards_count
                    self.update_cards_count.emit(cards_count)
                case Package.GetPlayer():
                    players = package.players
                    print(players)
                    self.update_players.emit(players)
                case _:
                    raise NotImplementedError


if __name__ == '__main__':

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    while True:
        type = int(input("Please choose type:"))

        match type:
            case 1:
                package = Package.PlayCard(evaluate_cards([1,10,11])[0])
            case 2:
                package = Package.PrevHand(evaluate_cards([1,10,11])[0])
            case 3:
                package = Package.InitCard([1,2,3,4,5,6,7,8,9,10])
            case 4:
                package = Package.GameOver('YuTse')
            case 5:
                package = Package.YourTurn(True)
            case 6:
                package = Package.ChkValid(evaluate_cards([1,10,11])[0])
            case 7:
                package = Package.ResValid(False)

        data = pickle.dumps(package)
        sock.send(data)
