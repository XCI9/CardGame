import socket
from utilities import *
import pickle
from package import Package
from PySide6.QtCore import Qt, Signal, QThread
from logger import ConnectionLogger
import struct
from typing import Optional
from game import LocalPlayerUtility, RemotePlayerUtility, PlayerUtilityInterface

class ClientHandler(QThread):
    gameover = Signal(str)
    update_players = Signal(list, int)
    connection_lose = Signal()
    sync_game = Signal(TableClassic, int)
    others_play_hand = Signal(Hand, int)
    others_erase_hand = Signal(int, int)

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
                case Package.GameOver():  self.gameover.emit(package.winner)
                case Package.GetPlayer(): self.update_players.emit(package.players, package.full_count)
                case Package.SyncGame():  self.sync_game.emit(package.table, package.id)
                case Package.PlayCard():  self.others_play_hand.emit(package.hand, package.id)
                case Package.PlayErase(): self.others_erase_hand.emit(package.card, package.id)
                case _:                    raise NotImplementedError
        self.logger.log('disconnect', self.socket, '')
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.connection_lose.emit()


class GameCoreClient:
    def __init__(self):
        self.initSocket()
        self.logger = ConnectionLogger('client')
        self.network_handler = ClientHandler(self.socket, self.logger)

    def initSocket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def resetSocket(self):
        self.initSocket()
        self.network_handler.socket = self.socket

    def connect(self, ip: str, port: int, name: str):
        self.socket.connect((ip, port))
        self.logger.log('connect', self.socket, '')

        self.network_handler.start()

        self.sendPackage(Package.SendName(name))

    def disconnnect(self):
        if self.socket.fileno() != -1:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
        if self.network_handler is not None:
            self.network_handler.wait()


    def sendPackage(self, package:Package.Package):
        package_byte = pickle.dumps(package)
        message_length = len(package_byte)
        header = struct.pack("!I", message_length)  # "!I" indicates network byte order for an unsigned int
        self.socket.sendall(header + package_byte)
        self.logger.log('send', self.socket, str(package))

    def getCurrentPlayer(self) -> Player:
        return self.current_player.player

    def setup(self, table: TableClassic, index: int):
        self.table = table
        self.players: list[PlayerUtilityInterface] = []
        
        for i, player in enumerate(self.table.players):
            if i != index:
                self.players.append(RemotePlayerUtility(player, self.table))
            else:
                self.current_player = LocalPlayerUtility(player, self.table)
                self.players.append(self.current_player)

    def selectCards(self, cards: list[int]):
        current_player = self.current_player

        if not current_player.for_erase:
            valid = current_player.select_cards(cards)

            if not valid:
                raise NotImplementedError
        else:
            if len(cards) == 1:
                if self.table.turn == 1 and 1 not in self.table.cards:
                    if cards[0] != 1:
                        return
                current_player.avalhands = [Hand((cards[0],))]
                current_player.avalhands_info = ['playable']

    def passTurn(self):
        current_player = self.current_player

        if self.current_player.for_erase:
            valid = current_player.play_erase(None)
            if valid:
                self.sendPackage(Package.PlayErase(-1, None))
        else:
            valid = current_player.pass_turn()
            if valid:
                self.sendPackage(Package.PlayCard(-1, None)) 

        if not valid:
            raise NotImplementedError
        
    def othersPlayHand(self, player_id: int, hand: Optional[Hand]) -> bool:
        current_player = self.players[player_id]

        if hand is None:
            return current_player.pass_turn()

        if len(current_player.player.cards) < len(hand.card):
            return False

        success = current_player.play_hand(hand)

        return success
    
    def othersEraseHand(self, player_id: int, card: Optional[int]) -> bool:
        current_player = self.players[player_id]

        success = current_player.play_erase(card)

        return success

    def playHand(self, hand: Hand):
        current_player = self.current_player

        # put played card onto table
        if current_player.for_erase:
            valid = current_player.play_erase(hand.card[0])
            self.sendPackage(Package.PlayErase(-1, hand.card[0]))
        else:
            valid = current_player.play_hand(hand)
            self.sendPackage(Package.PlayCard(-1, hand))

        if not valid:
            raise NotImplementedError

    def getRule(self) -> tuple[bool, bool, bool]:
        return self.table.rule9, self.table.rule19, self.table.rule29
