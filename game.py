from typing import Optional
from utilities import TableClassic, Player, Hand, evaluate_cards


class PlayerUtilityInterface:
    """An interface for player utilities at each side.
    
    For server side to record and monitoring players: 
        PlayerUtility
        --- Provides checking for each action.
    For player himself at his side : 
        LocalPlayerUtility
        --- Inherit `PlayerUtility`, it provides additional real time
            hands info (hand hint and playable hint).
    For player at his side to see other players: 
        RemotePlayerUtility
        --- Provides no checking, implement minima necessary action to 
            update the game.
    """
    def __init__(self, player: Player, table: TableClassic):
        self.player = player
        self.table = table
    def pass_turn(self):
        raise NotImplementedError(
            'pure virtual function not overwritten.'
        )
    def play_hand(self, hand: Hand) -> bool:
        raise NotImplementedError(
            'pure virtual function not overwritten.'
        )
    def play_erase(self, card: Optional[int]) -> bool:
        raise NotImplementedError(
            'pure virtual function not overwritten.'
        )

class PlayerUtility(PlayerUtilityInterface):
    """A panel for player in server, used as record, monitoring and sync.
    
    This class is used in server side to record and monitoring players.
    It checks the validity of each action, it's a standard set of utilities
    for game to go on.
    """
    def __init__(self, player: Player, table: TableClassic) -> None:
        super().__init__(player, table)
        self.for_erase = False
    def pass_turn(self) -> bool:
        """A player pass his turn.
        
        It will check whether a player is allowed to pass his turn.
        """
        if self.player.lastplayed:
            return False
        else:
            self.table.turn_forward(played_hand=False)
            return True
    def play_hand(self, hand: Hand) -> bool:
        """A player plays a hand onto table.
        
        It checks whether the timing is right, 
        checks whether a player has those cards,
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
    def play_erase(self, card: Optional[int]) -> bool:
        """A player erase a card.
        
        For turn 1, it checks whether it is allowed to erase a card.
        """
        if not self.for_erase:
            return False
        if self.table.turn == 1 and 1 not in self.table.cards:
            if card != 1:
                return False

        if card not in (-1, None):
            self.player.remove_cards([card])
            self.table.erase(card)
        self.table.turn_forward(played_hand=True)
        self.for_erase = False
        return True

class RemotePlayerUtility(PlayerUtilityInterface):
    """A panel for remote players. it provides no checking.
    
    This class is used as utility for a player in his side to see other players.
    It provides no checking at all, implement minima necessary action to update 
    the game.
    """
    def __init__(self, player: Player, table: TableClassic) -> None:
        super().__init__(player, table)
    def play_hand(self, hand: Hand) -> bool:
        """A remote player play a hand.
        
        Play a hand on to table, with no checking.
        """
        self.player.remove_cards([-1 for card in hand.card])
        self.table.play_hand(hand)
        if not hand.eraseable:
            self.table.turn_forward(played_hand=True)
        return True
    def play_erase(self, card: Optional[int]) -> bool:
        """A remote player play a erase card.
        
        Erase a card onto table, with no checking.
        """
        if card not in (-1, None):
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

class LocalPlayerUtility(PlayerUtility, PlayerUtilityInterface):
    """"A panle for local players. It provides checking and real time hands info.
    
    This class is used as a player utility himself at his side.
    It uses stander set of utilitits that provides checking, and it provides 
    additional real time hands info (hand hint and playable hint).
    """
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
        
        It checks whether a player have the selected cards in hand,
        then update hands info.
        """
        if any(card not in self.player.cards for card in cards):
            return False
        self.player.selected_cards = cards
        if not self.for_erase:
            self.update_handsinfo()
        return True