import socket
from game import *
import pickle
from package import Package
from PySide6.QtCore import Qt, Signal, QThread
from ConnectionLogger import ConnectionLogger

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

    def __init__(self, socket: socket.socket, logger: ConnectionLogger):
        super().__init__()
        self.socket = socket
        self.logger = logger

    def run(self):
        while True:
            data = self.socket.recv(1024)
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
                case Package.GetPlayer():  self.update_players.emit(package.players)
                case _:                    raise NotImplementedError


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
