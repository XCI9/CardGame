from utilities import *
from typing import Callable, Optional
from functools import singledispatchmethod
from utilities import TableClassic


class PlayerUtility:
    """A panel for player in serve, used as checking and sync."""
    def __init__(self, player: Player, table: TableClassic) -> None:
        self.player = player
        self.table = table
    def pass_turn(self) -> bool:
        """A player pass his turn.
        
        It will check wheter a player is allowed to pass his turn.
        """
        if self.player.lastplayed:
            return False
        else:
            self.table.turn_forward(played_hand=False)
            return True
    def play_hand(self, hand: Hand) -> bool:
        """A player plays a hand on to table.
        
        It checks whether the timing is right, 
        checks wheter a player has those cards,
        and checks if the hand is playable.
        """
        cards_tbp = hand.card
        if self.for_erase:
            return False
        if any(card not in self.player.cards for card in cards_tbp):
            return False
        if not self.table.is_playable_hand(hand):
            return False
        self.table.play_hand(hand)
        self.player.remove_cards(cards_tbp)
        if not hand.eraseable:
            self.table.turn_forward(played_hand=True)
        else:
            self.for_erase = True
        return True
    def play_erase(self, card: int) -> bool:
        """A player erase a card.
        
        For turn 1, it checks whether it is allowed to erase a card.
        """
        if not self.for_erase:
            return False
        if self.table.turn == 1 and 1 not in self.table.cards:
            if card != 1:
                return False
        self.table.erase(card)
        self.table.turn_forward(played_hand=True)
        self.player.remove_cards([card])
        self.for_erase = False
        return True

class RemotePlayerUtility:
    """An panle for remote players (every other playes)."""
    def __init__(self, player: Player, table: TableClassic) -> None:
        self.player = player
        self.table = table
    def play_hand(self, hand: Hand) -> bool:
        """A remote player play a hand.
        
        Play a hand on to table, with no checking.
        """
        self.player.remove_cards([-1 for card in hand.card])
        self.table.play_hand(hand)
        if not hand.eraseable:
            self.table.turn_forward(played_hand=True)
        return True
    def play_erase(self, card: int):
        """A remote player play a erase card.
        
        Erase a card onto table, with no checking.
        """
        self.player.remove_cards([-1])
        self.table.erase(card)
        self.table.turn_forward(played_hand=True)
        return True
    def pass_turn(self) -> bool:
        """A remote player pass his turn.
        
        Make turn forward, with no checking.
        """
        self.table.turn_forward(played_hand=False)
        return True

class LocalPlayerUtility(PlayerUtility):
    def __init__(self, player: Player, table: TableClassic) -> None:
        super().__init__(player, table)
        self.avalhands:list[Hand] = []
        self.avalhands_info:list[str] = []
    def update_handsinfo(self):
        """Update information about hands, avaliable and playable.

        It evaluate avaliable hands, set value of `self.avalhands` to them.
        For n-th element of `self.avalhands` is playable for the table, n-th 
        element of `self.avalhands_info` will be 'playable', it contains
        the reason of unplayable otherwise.
        """
        self.avalhands = []
        self.avalhands_info = []
        avalhands = evaluate_cards(self.player.selected_cards)
        self.avalhands = avalhands
        for avalhand in avalhands:
            playable, info = self.table.is_playable_hand(avalhand)
            if playable:
                self.avalhands_info.append('playable')
            else:
                self.avalhands_info.append(info)
    def select_cards(self, cards: list[int]) -> bool:
        """Call this function when a player change selected cards.
        
        It checks wheter a player have the selected cards in hand,
        then update hands info.
        """
        if any(card not in self.player.cards for card in cards):
            return False
        self.player.selected_cards = cards
        if not self.for_erase:
            self.update_handsinfo()
        return True


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

    def playHand(self, player_index:int, hand: Hand) -> bool:
        current_player = self.players[player_index]
        if not self._yourTurn(current_player):
            return False
        
        if current_player.for_erase:
            return current_player.play_erase2(hand)
        else:
            return current_player.play_hand2(hand)
    
    def passTurn(self, player_index:int):
        current_player = self.players[player_index]
        if not self._yourTurn(current_player):
            return False
        return current_player.pass_turn() 
    
    def allPlayerReady(self):
        """Return if all players are ready to play the games"""
        return all(self.allow_start)

class GameCoreClient:
    def getCurrentPlayer(self) -> Player:
        return self.current_player.player

    def setup(self, table: TableClassic, index: int):
        self.table = table
        self.players: list[PlayerUtility] = []
        
        for player in self.table.players:
            self.players.append(PlayerUtility(player, self.table))
        
        self.current_player = self.players[index]

    def selectCards(self, cards: list[int]):
        current_player = self.current_player

        if not current_player.for_erase:
            valid = current_player.select_cards(cards)

            if not valid:
                raise NotImplementedError
        else:
            if len(cards) == 1:
                current_player.avalhands = [Hand((cards[0],))]
                current_player.avalhands_info = ['playable']

    def passTurn(self):
        current_player = self.current_player

        valid = current_player.pass_turn()

        if not valid:
            raise NotImplementedError
        
    def othersPlayHand(self, player_id: int, hand: Optional[Hand]) -> bool:
        current_player = self.players[player_id]

        if hand is None:
            return current_player.pass_turn()

        if len(current_player.player.cards) < len(hand.card):
            return False

        current_player.player.cards[:len(hand.card)] = hand.card

        if not current_player.for_erase:
            success = current_player.play_hand2(hand)
        else:
            success = current_player.play_erase2(hand)

        return success

    def playHand(self, index: int):
        current_player = self.current_player

        if not current_player.for_erase:
            selectable = current_player.select_hand(index)

            if not selectable:
                raise NotImplementedError

            current_player.play_hand()
        else:
            current_player.play_erase()

    def getRule(self) -> tuple[bool, bool, bool]:
        return self.table.rule9, self.table.rule19, self.table.rule29
    

