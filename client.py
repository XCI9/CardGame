from utilities import TableClassic, Hand
import pickle
from package import Package
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtNetwork import QTcpSocket, QAbstractSocket
from logger import ConnectionLogger
import struct
from typing import Optional
from game import LocalPlayerUtility, RemotePlayerUtility, PlayerUtilityInterface

class ClientHandler(QObject):
    gameover = Signal(str)
    update_players = Signal(list, int)
    connection_lose = Signal()
    sync_game = Signal(TableClassic, int)
    others_play_hand = Signal(Hand, int)
    others_erase_hand = Signal(int, int)
    connection_error = Signal(str)

    def __init__(self):
        super().__init__()
        self.socket = QTcpSocket()
        self.socket.readyRead.connect(self.on_ready_read)
        self.socket.disconnected.connect(self.on_disconnected)
        self.socket.connected.connect(self.on_connected)
        self.socket.errorOccurred.connect(self.on_error)

        self.logger = ConnectionLogger('client')

    def connect_to_server(self, ip: str, port:int, name: str):
        self.socket.connectToHost(ip, port)
        self.name = name
        
    def disconnect_from_server(self):
        self.socket.disconnectFromHost()

    def on_connected(self):
        self.logger.log('connect', self.socket, '')
        self.sendPackage(Package.SendName(self.name))

    def on_ready_read(self):
        header = self.socket.read(4).data()  # Read the 4-byte header
        length = struct.unpack("!I", header)[0]  # Unpack the message length from network byte order
        data = self.socket.read(length).data()
        package = pickle.loads(data)
        self.logger.log('recv', self.socket, str(package))

        match package:
            case Package.GameOver():  self.gameover.emit(package.winner)
            case Package.GetPlayer(): self.update_players.emit(package.players, package.full_count)
            case Package.SyncGame():  self.sync_game.emit(package.table, package.id)
            case Package.PlayCard():  self.others_play_hand.emit(package.hand, package.id)
            case Package.PlayErase(): self.others_erase_hand.emit(package.card, package.id)
            case _:                    raise NotImplementedError
        
    def on_disconnected(self):
        self.logger.log('disconnect', self.socket, '')
        self.connection_lose.emit()

    def on_error(self, socketError):
        if socketError == QAbstractSocket.SocketError.ConnectionRefusedError:
            self.connection_error.emit('連線請求被伺服器拒絕')
        else:
            self.connection_error.emit(f'連線錯誤:{socketError}')

    def sendPackage(self, package:Package.Package):
        package_byte = pickle.dumps(package)
        message_length = len(package_byte)
        header = struct.pack("!I", message_length)  # "!I" indicates network byte order for an unsigned int
        self.socket.write(header + package_byte)
        self.logger.log('send', self.socket, str(package))

class GameCoreClient:
    def __init__(self):
        self.network_handler = ClientHandler()

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
                self.network_handler.sendPackage(Package.PlayErase(-1, None))
        else:
            valid = current_player.pass_turn()
            if valid:
                self.network_handler.sendPackage(Package.PlayCard(-1, None)) 

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
            self.network_handler.sendPackage(Package.PlayErase(-1, hand.card[0]))
        else:
            valid = current_player.play_hand(hand)
            self.network_handler.sendPackage(Package.PlayCard(-1, hand))

        if not valid:
            raise NotImplementedError

    def getRule(self) -> tuple[bool, bool, bool]:
        return self.table.rule9, self.table.rule19, self.table.rule29
    
    def playAgain(self):
        self.network_handler.sendPackage(Package.AgainChk(True))
