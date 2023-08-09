import socketserver
import socket
from package import Package
import pickle
from game import *
import threading
import time
from ConnectionLogger import ConnectionLogger


class ServerHandler(socketserver.BaseRequestHandler):
    clients:dict[socket.socket, int] = {}
    game_core = TableClassic()
    end_players = []
    logger = ConnectionLogger('server')
    used_name = set()

    def sendPackage(self, client:socket.socket, package):
        #print(f'send package: {package}')
        self.logger.log('send', client, str(package))
        package_byte = pickle.dumps(package)
        client.send(package_byte)

    def startGame(self):
        success = self.game_core.start()
        
        if not success:
            return success
        
        for client, i in self.clients.items():
            cards = self.game_core.players[i].cards
            self.sendPackage(client, Package.InitCard(cards))
        time.sleep(0.1)
        self.updateCardCount()
        self.notifyNextTurnPlayer()

    def notifyNextTurnPlayer(self):
        # told player who has one "It's his turn"
        current_turn_index = -1
        for client, i in self.clients.items(): 
            if self.game_core.players[i].his_turn:
                self.sendPackage(client, Package.YourTurn(self.game_core.players[i].lastplayed))
                current_turn_index = i
                break

        for client, i in self.clients.items():
            if i != current_turn_index:
                self.sendPackage(client, Package.ChangeTurn(self.game_core.players[current_turn_index].name)) 

    def updateCardCount(self):
        cards_count = []
        for player in self.game_core.players:
            cards_count.append((player.name, len(player.cards)))

        package = Package.CardLeft(cards_count)
        for client, i in self.clients.items():
            self.sendPackage(client, package)

    def playHand(self, hand:Hand, player_index: int):
        if hand is not None:
            self.game_core.play_hand(hand)
            for card in hand.card:
                self.game_core.players[player_index].cards.remove(card)

            if hand.erased_card is not None:
                self.game_core.erase(hand.erased_card)
                self.game_core.players[player_index].cards.remove(hand.erased_card)
                #print(self.game_core.players[player_index].cards)

            # update table for all player
            package = Package.PrevHand(hand)
            for client in self.clients.keys():
                self.sendPackage(client, package)

        self.game_core.turn_forward(hand is not None)

        # game end
        if self.game_core.game_playing is False:
            win_player_name = self.game_core.players[self.end_players[0]].name
            for client, i in self.clients.items():
                if i == self.end_players[0]:
                    package = Package.GameOver('你')
                else:
                    package = Package.GameOver(win_player_name)
                self.sendPackage(client, package)
            return

        self.notifyNextTurnPlayer()

        if len(self.game_core.players[player_index].cards) == 0:
            self.end_players.append(player_index)

        # update card of each player
        self.updateCardCount()

    def updatePlayer(self):
        players = []
        for player in self.game_core.players:
            players.append(player.name)

        #print(players)
        package = Package.GetPlayer(players)
        for client, i in self.clients.items():
            self.sendPackage(client, package)  

    def evaluateHands(self, hands:Hand):
        results = []
        for hand in hands:
            valid, reason = self.game_core.is_playable_hand(hand)
            results.append((hand, valid, reason))
        self.sendPackage(self.request, Package.ResValid(results))

    def closeConnection(self, reason:str):
        self.logger.log('disconnect', self.request, reason)
        del self.game_core.players[self.clients[self.request]]
        del self.clients[self.request]
        
        self.updatePlayer()
        self.request.shutdown(socket.SHUT_RDWR)
        self.request.close()

    def initPlayerName(self, name:str):
        if name in self.used_name:
            self.closeConnection(f'"{name}" is a collision name')
            return
        self.used_name.add(name)
        index = self.clients[self.request]
        self.game_core.players[index].name = name

        self.updatePlayer()
        if len(self.clients) == 3:
            self.startGame() 
            
    def handle(self):
        self.logger.log('connect', self.request, '')
        accept = self.game_core.join(Player())
        
        self.clients[self.request] = len(self.clients)  
        player_index = self.clients[self.request]

        if not accept:
            self.closeConnection('player not accept')
            return
        while self.request.fileno() != -1:
            # self.request is the TCP socket connected to the client
            try:
                self.data = self.request.recv(1024)
                if not self.data:
                    self.closeConnection('player disconnect')
                    break
            except (ConnectionResetError, OSError):
                self.closeConnection('player disconnect')
                break

            package = pickle.loads(self.data)
            self.logger.log('recv', self.request, str(package))
            
            match package:
                case Package.PlayCard(): self.playHand(package.hand, player_index)
                case Package.ChkValid(): self.evaluateHands(package.hands)
                case Package.SendName(): self.initPlayerName(package.name)
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
    



    
