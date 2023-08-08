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

        for client, i in self.clients.items():
            if i != current_turn_index:
                package = pickle.dumps(Package.ChangeTurn(self.game_core.players[current_turn_index].name))
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

                        if hand.erased_card is not None:
                            self.game_core.erase(hand.erased_card)
                    self.game_core.turn_forward(hand is not None)
                    self.notifyNextTurnPlayer()

                    # update table for all player
                    if self.game_core.get_player(-1).lastplayed:
                        prev_hand = self.game_core.previous_hand
                        package = pickle.dumps(Package.PrevHand(prev_hand))
                        for client in self.clients.keys():
                            client.send(package)
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
    



    
