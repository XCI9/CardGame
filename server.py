import socketserver
import socket
from package import Package
import pickle
from utilities import *
import threading
import struct
from logger import ConnectionLogger
from game import PlayerUtility
from copy import deepcopy
from typing import Optional

class GameCoreServer: 
    def __init__(self) -> None:
        self.table = TableClassic()
        self.players: list[PlayerUtility] = []
        self.names:set[str] = set()
        self.winner = None
        
        self.max_player_count = 3
        self.allow_start: list[bool] = []

    def start(self):
        self.winner = None
        return self.table.start()

    def getPlayersName(self) -> list[str]:
        """Return all exists players' name"""
        names = []
        for player in self.table.players:
            names.append(player.name)

        return names

    def getPlayerById(self, id:int) -> Player:
        """Return player object given id"""
        return self.table.players[id]

    def getNextTurnPlayer(self) -> int:
        """Return next player id, should be called after turn_forward """
        for i, player in enumerate(self.table.players):
            if player.his_turn:
                return i
        raise NotImplementedError

    def setName(self, player_id:int, name:str) -> bool:
        """Return if the name is set successfully"""
        if name in self.names:
            return False
        self.names.add(name)

        self.table.players[player_id].name = name
        return True

    def isPlayerFull(self) -> bool:
        """Return if the game is full and so cannot join new player"""
        return len(self.table.players) == self.max_player_count

    def join(self) -> int:
        """Return player id if join success, -1 if failed"""
        player = Player()
        accept = self.table.join(player)

        if accept:
            self.allow_start.append(True)
            self.players.append(PlayerUtility(player, self.table))
            return len(self.table.players) - 1
        return -1

    def leave(self, player_index: int):
        """Delete the player from the game"""
        del self.table.players[player_index]
        del self.allow_start[player_index]
        del self.players[player_index]

    @staticmethod
    def _yourTurn(player:PlayerUtility):
        return player.player.his_turn

    def playHand(self, player_index: int, hand: Hand) -> bool:
        current_player = self.players[player_index]
        if not self._yourTurn(current_player):
            return False
        
        return current_player.play_hand(hand)
        
    def playErase(self, player_index: int, card: int) -> bool:
        current_player = self.players[player_index]
        if not self._yourTurn(current_player):
            return False
        
        return current_player.play_erase(card)
    
    def passTurn(self, player_index:int):
        current_player = self.players[player_index]
        if not self._yourTurn(current_player):
            return False
        return current_player.pass_turn() 
    
    def allPlayerReady(self):
        """Return if all players are ready to play the games"""
        return all(self.allow_start)


class ServerHandler(socketserver.BaseRequestHandler):
    clients:list[socket.socket] = []
    core = GameCoreServer()
    logger = ConnectionLogger('server')
    init = False

    def setPlayerCount(self, count: int):
        self.core.max_player_count = count

    def sendPackage(self, client:socket.socket, package: Package.Package):
        #print(f'send package: {package}')
        self.logger.log('send', client, str(package))
        package_byte = pickle.dumps(package)
        message_length = len(package_byte)
        header = struct.pack("!I", message_length)  # "!I" indicates network byte order for an unsigned int
        client.sendall(header + package_byte)

    def broadcastPackage(self, package: Package.Package):
        for client in self.clients:
            self.sendPackage(client, package)

    def broadcastPackageExcept(self, package: Package.Package, 
                               except_id :int, except_package: Optional[Package.Package] = None):
        for id, client in enumerate(self.clients):
            if id == except_id:
                if except_package is not None:
                    self.sendPackage(client, except_package)
            else:
                self.sendPackage(client, package)

    def syncGame(self):
        for id, client in enumerate(self.clients):
            self.syncGameTo(id)

    def syncGameTo(self, player_id:int):
        id = player_id

        table = deepcopy(self.core.table)
        for i in range(len(table.players)):
            if i != id:
                table.players[i].cards = [-1] * len(table.players[i].cards)
        package = Package.SyncGame(table,id)
        self.sendPackage(self.clients[id], package)

    def startGame(self):
        success = self.core.start()
        
        if not success:
            return success
        
        self.syncGame()

    def gameover(self, winner_id: int):
        winner = self.core.getPlayerById(winner_id)
        self.broadcastPackageExcept(Package.GameOver(winner.name),
                                    winner_id, Package.GameOver('你'))
        for i in range(len(self.clients)):
            self.core.allow_start[i] = False

    def playHand(self, player_id: int, hand: Hand):
        if hand is None:
            success = self.core.passTurn(player_id)
        else:
            success = self.core.playHand(player_id, hand)
            
        if not success:
            self.syncGameTo(player_id)
            return

        # update table for all player
        self.broadcastPackageExcept(Package.PlayCard(player_id, hand), player_id)

    def playErase(self, player_id: int, card: int):
        success = self.core.playErase(player_id, card)
            
        if not success:
            self.syncGameTo(player_id)
            return

        # update table for all player
        self.broadcastPackageExcept(Package.PlayErase(player_id, card), player_id)

    def updatePlayer(self):
        self.broadcastPackage(Package.GetPlayer(self.core.getPlayersName(), self.core.max_player_count))

    def closeConnection(self, player_id:int, reason:str):
        self.logger.log('disconnect', self.request, reason)
        self.core.leave(player_id)
        del self.clients[player_id]
        
        self.updatePlayer()
        self.request.shutdown(socket.SHUT_RDWR)
        self.request.close()

    def initPlayerName(self, player_id:int, name:str):
        success = self.core.setName(player_id, name)
        if not success:
            self.closeConnection(player_id, f'"{name}" is a collision name')
            return

        self.updatePlayer()
        if self.core.isPlayerFull() and self.core.allPlayerReady():
            self.startGame() 

    def againCheck(self, player_id:int, reply: bool):
        if reply is True:
            print(self.core.allow_start, player_id)
            self.core.allow_start[player_id] = True
            if self.core.allPlayerReady() and self.core.isPlayerFull():
                self.startGame()
        else:
            self.closeConnection(player_id, 'leave game')

            
    def handle(self):
        # Only run at first time
        if not self.init:
            self.init = True
            self.setPlayerCount(self.server.player_count)

        self.logger.log('connect', self.request, '')
        player_id = self.core.join()
        if player_id == -1:
            self.logger.log('disconnect', self.request, 'join not accept')
            return
        
        self.request.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        
        self.clients.append(self.request)
        while self.request.fileno() != -1:
            # self.request is the TCP socket connected to the client
            try:
                header = self.request.recv(4)  # Read the 4-byte header
                if not header:
                    self.closeConnection(player_id, 'player disconnect')
                    break
                length = struct.unpack("!I", header)[0]  # Unpack the message length from network byte order
                self.data = self.request.recv(length)

            except (ConnectionResetError, OSError):
                self.closeConnection(player_id, 'player disconnect')
                break
            player_id = self.clients.index(self.request)

            package = pickle.loads(self.data)
            self.logger.log('recv', self.request, str(package))

            match package:
                case Package.PlayCard(): self.playHand(player_id, package.hand)
                case Package.SendName(): self.initPlayerName(player_id, package.name)
                case Package.AgainChk(): self.againCheck(player_id, package.agree)
                case Package.PlayErase():self.playErase(player_id, package.card)
                case _:                  raise NotImplementedError

def startServer(host:str, port:int, player_count:int):
    server = socketserver.ThreadingTCPServer((host, port), ServerHandler)
    server.player_count = player_count
    print(f'serve on {host}:{port}')

    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

if __name__ == '__main__':
    host = "127.0.0.1"
    port = 8888
    player_count = 3

    startServer(host, port, player_count)
    input()  
