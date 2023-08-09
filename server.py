import socketserver
import socket
from package import Package
import pickle
from game import *
import threading
import time
import debugpy


class ServerHandler(socketserver.BaseRequestHandler):
    clients:dict[socket.socket, int] = {}
    game_core = TableClassic()
    end_players = []
    """
    The RequestHandler class for our server.
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def startGame(self):
        success = self.game_core.start()
        
        if not success:
            return success
        
        for client, i in self.clients.items():
            cards = self.game_core.players[i].cards
            package = pickle.dumps(Package.InitCard(cards))
            client.send(package)
        time.sleep(0.1)
        self.updateCardCount()
        self.notifyNextTurnPlayer()

    def notifyNextTurnPlayer(self):
        # told player who has one "It's his turn"
        current_turn_index = -1
        for client, i in self.clients.items(): 
            if self.game_core.players[i].his_turn:
                print(f'turn {self.game_core.players[i].his_turn}')
                package = pickle.dumps(Package.YourTurn(self.game_core.players[i].lastplayed))
                client.send(package)
                current_turn_index = i
                
                break
        
        in_game_count = 0
        for player in self.game_core.players:
            if player.in_game:
                in_game_count += 1

        if in_game_count <= 1:
            win_player_name = self.game_core.players[self.end_players[0]].name
            for client, i in self.clients.items():
                if i == self.end_players[0]:
                    package = pickle.dumps(Package.GameOver('你'))
                else:
                    package = pickle.dumps(Package.GameOver(win_player_name))
                client.send(package)


        for client, i in self.clients.items():
            if i != current_turn_index:
                package = pickle.dumps(Package.ChangeTurn(self.game_core.players[current_turn_index].name))
                client.send(package)    

    def updateCardCount(self):
        cards_count = []
        for player in self.game_core.players:
            cards_count.append((player.name, len(player.cards)))

        package = pickle.dumps(Package.CardLeft(cards_count))
        for client, i in self.clients.items():
            client.send(package)        
            
    def handle(self):
        debugpy.debug_this_thread()
        print(f'client {self.client_address[0]}:{self.client_address[1]} connect')
        accept = self.game_core.join(Player())
        if not accept:
            self.request.shutdown(socket.SHUT_RDWR)
            self.request.close()
            return
        
        self.clients[self.request] = len(self.clients)  
        player_index = self.clients[self.request]

        while True:
            # self.request is the TCP socket connected to the client
            self.data = self.request.recv(1024)
            if not self.data:
                break
            package = pickle.loads(self.data)
            
            match package:
                case Package.PlayCard():
                    hand: Hand = package.hand
                    if hand is not None:
                        self.game_core.play_hand(hand)
                        for card in hand.card:
                            self.game_core.players[player_index].cards.remove(card)

                        if hand.erased_card is not None:
                            self.game_core.erase(hand.erased_card)
                            self.game_core.players[player_index].cards.remove(hand.erased_card)
                            print(self.game_core.players[player_index].cards)

                        # update table for all player
                        package = pickle.dumps(Package.PrevHand(hand))
                        for client in self.clients.keys():
                            client.send(package)

                    self.game_core.turn_forward(hand is not None)
                    self.notifyNextTurnPlayer()

                    if len(self.game_core.players[player_index].cards) == 0:
                        self.end_players.append(player_index)

                    # update card of each player
                    self.updateCardCount()
                case Package.ChkValid():
                    hands = package.hands

                    results = []
                    for hand in hands:
                        valid, reason = self.game_core.is_playable_hand(hand)
                        results.append((hand, valid, reason))
                    reply_package = Package.ResValid(results)
                    self.request.send(pickle.dumps(reply_package)) 
                case Package.SendName():
                    name = package.name
                    print(name)
                    index = self.clients[self.request]
                    self.game_core.players[index].name = name
                    if len(self.clients) == 3:
                        self.startGame() 
                case _:
                    raise NotImplementedError
        print(f'client {self.client_address[0]}:{self.client_address[1]} disconnect')
        del self.clients[self.request]

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
    



    
