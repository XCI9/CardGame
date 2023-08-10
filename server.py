import socketserver
import socket
from package import Package
import pickle
from game import *
import threading
import time
from logger import ConnectionLogger

class GameCore:
    def __init__(self):
        self.core = TableClassic()
        self.winner = None
        self.names = set()
        self.allow_start = []

    def start(self):
        return self.core.start()
    
    def getPlayerById(self, id) -> Player:
        return self.core.players[id]
    
    """
    Return if the name is set successfully
    """
    def setName(self, player_id:int, name:str) -> bool:
        if name in self.names:
            return False
        self.names.add(name)

        self.core.players[player_id].name = name
        return True

    def isPlayerFull(self) -> bool:
        return len(self.core.players) == 3

    """
    Return player id if join success, -1 if failed
    """
    def join(self):
        accept = self.core.join(Player())

        if accept:
            self.allow_start.append(True)
            return len(self.core.players) - 1
        return -1
    
    def leave(self, player_id: int):
        del self.core.players[player_id]
        del self.allow_start[player_id]

    def playHand(self, player_id:int, hand: Hand):
        id = player_id
        if hand is None:
            return
        
        self.core.play_hand(hand)
        for card in hand.card:
            self.core.players[id].cards.remove(card)

        if hand.erased_card is not None:
            self.core.erase(hand.erased_card)
            self.core.players[id].cards.remove(hand.erased_card)

        # first one to clear all cards is the winner
        if self.winner is None and len(self.core.players[id].cards) == 0:
            self.winner = id

    def getCardCounts(self):
        cards_count = []
        for player in self.core.players:
            cards_count.append((player.name, len(player.cards)))

        return cards_count
    
    def getPlayersName(self):
        names = []
        for player in self.core.players:
            names.append(player.name)

        return names

    def evaluateHands(self, hands:Hand):
        results = []
        for hand in hands:
            valid, reason = self.core.is_playable_hand(hand)
            results.append((hand, valid, reason))

        return results
    
    """
    Return next player id, should be called after turn_forward
    """
    def getNextTurnPlayer(self) -> int:
        for i, player in enumerate(self.core.players):
            if player.his_turn:
                return i

    """
    Return the winner id if the game end, else return None
    """
    def turn_forward(self, is_last_player_pass:bool):
        self.core.turn_forward(is_last_player_pass)

        if self.core.game_playing is False:
            return self.winner
        
        return None

    def allPlayerReady(self):
        return all(self.allow_start)


class ServerHandler(socketserver.BaseRequestHandler):
    clients:list[socket.socket] = []
    core = GameCore()
    logger = ConnectionLogger('server')

    def sendPackage(self, client:socket.socket, package: Package.Package):
        #print(f'send package: {package}')
        self.logger.log('send', client, str(package))
        package_byte = pickle.dumps(package)
        client.send(package_byte)

    def broadcastPackage(self, package: Package.Package):
        for client in self.clients:
            self.sendPackage(client, package)

    def broadcastPackageExcept(self, package: Package.Package, 
                               except_id :int, except_package: Package.Package):
        for id, client in enumerate(self.clients):
            if id == except_id:
                self.sendPackage(client, except_package)
            else:
                self.sendPackage(client, package)

    def startGame(self):
        success = self.core.start()
        
        if not success:
            return success
        
        for id, client in enumerate(self.clients):
            package = Package.InitCard(self.core.getPlayerById(id).cards)
            self.sendPackage(client, package)

        time.sleep(0.1)
        self.updateCardCount()
        self.notifyNextTurnPlayer()

    def notifyNextTurnPlayer(self):
        next_turn_id = self.core.getNextTurnPlayer()
        next_turn_player = self.core.getPlayerById(next_turn_id)

        self.broadcastPackageExcept(Package.ChangeTurn(next_turn_player.name), 
                                    next_turn_id, Package.YourTurn(next_turn_player.lastplayed))

    def updateCardCount(self):
        cards_count = self.core.getCardCounts()

        self.broadcastPackage(Package.CardLeft(cards_count))

    def gameover(self, winner_id: int):
        winner = self.core.getPlayerById(winner_id)
        self.broadcastPackageExcept(Package.GameOver(winner.name),
                                    winner_id, Package.GameOver('你'))
        for i in range(len(self.clients)):
            self.core.allow_start[i] = False

    def playHand(self, player_id: int, hand:Hand):
        if hand is not None:
            self.core.playHand(player_id, hand)

            # update table for all player
            self.broadcastPackage(Package.PrevHand(hand))

        winner_id = self.core.turn_forward(hand is not None)

        # game end
        if winner_id is not None:
            self.gameover(winner_id)

        self.notifyNextTurnPlayer()

        # update card of each player
        self.updateCardCount()

    def updatePlayer(self):
        self.broadcastPackage(Package.GetPlayer(self.core.getPlayersName()))

    def evaluateHands(self, hands:Hand):
        package = Package.ResValid(self.core.evaluateHands(hands))
        self.sendPackage(self.request, package)

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
        self.logger.log('connect', self.request, '')
        player_id = self.core.join()
        if player_id == -1:
            self.logger.log('disconnect', self.request, 'join not accept')
            return
        
        self.clients.append(self.request)
        while self.request.fileno() != -1:
            # self.request is the TCP socket connected to the client
            try:
                self.data = self.request.recv(1024)
                if not self.data:
                    self.closeConnection(player_id, 'player disconnect')
                    break
            except (ConnectionResetError, OSError):
                self.closeConnection(player_id, 'player disconnect')
                break
            player_id = self.clients.index(self.request)

            package = pickle.loads(self.data)
            self.logger.log('recv', self.request, str(package))
            
            match package:
                case Package.PlayCard(): self.playHand(player_id, package.hand)
                case Package.ChkValid(): self.evaluateHands(package.hands)
                case Package.SendName(): self.initPlayerName(player_id, package.name)
                case Package.AgainChk(): self.againCheck(player_id, package.agree)
                case _:                  raise NotImplementedError

def startServer(host, port):
    server = socketserver.ThreadingTCPServer((host, port), ServerHandler)
    print(f'serve on {host}:{port}')

    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

if __name__ == '__main__':
    host = "127.0.0.1"
    port = 8888

    startServer(host, port)
    input()  
