from utilities import *


class PlayerUtility:
    def __init__(self, player: Player, table: TableClassic) -> None:
        self.table = table
        self.player = player
        self.for_erase = False
        # UI
        self.avalhands = []
        self.avalhands_info = []
    def update_handsinfo(self):
        """Update information about hands, avaliable and playable.

        It evaluate avaliable hands, set value of `self.avalhands` to them.
        For n-th element of `self.avalhands` is playable for the table, n-th 
        element of `self.avalhands_info` will be 'playable', it contains
        the reason of unplayable otherwise.
        """
        self.avalhands = []
        self.avalhands_info = []
        avalhands = evaluate_cards(self.select_cards)
        for avalhand in avalhands:
            playable, info = self.table.is_playable_hand(avalhand)
            if playable:
                self.avalhands_info.append('playable')
            else:
                self.avalhands_info.append(info)
    def select_cards(self, cards: tuple) -> bool:
        """Call this function when a player change selected cards."""
        if any(card not in self.player.cards for card in cards):
            return False
        self.player.selected_cards = cards
        if not self.for_erase:
            self.update_handsinfo()
        return True
    def select_hand(self, index: int) -> bool:
        """Call this function when a player select a hand.
        Argument: index, int
            index to acess `self.avalhands` and `self.avalhands_info`.
        """
        if not self.avalhands_info[index] == 'playable':
            return False
        self.player.selected_hand = self.avalhands[index]
        return True

    def pass_turn(self) -> bool:
        """Call this method when a player press 'pass'"""
        if self.player.lastplayed:
            return False
        self.table.turn_forward(played_hand=False)
        return True
    def play_hand(self) -> bool:
        """Call this method when a player press '打出'."""
        hand_tbp = self.player.selected_hand
        if hand_tbp == None:
            return False
        self.table.play_hand(hand_tbp)
        self.player.remove_cards(hand_tbp.card)
        if not hand_tbp.eraseable:
            self.table.turn_forward(played_hand=True)
        else:
            pass
        return True
    def play_erase(self) -> bool:
        """Call this method when a player press '消除'."""
        if len(self.player.selected_cards) != 1:
            return False
        card_tbp = self.player.selected_cards[0]
        if self.table.turn == 1 and 1 not in self.table:
            if card_tbp != 1:
                return False
        self.table.erase(card_tbp)
        self.table.turn_forward(played_hand=True)
        self.for_erase = False
        return True

class GameCore: 
    def __init__(self, table: TableClassic) -> None:
        self.table = table
        self.p: list[PlayerUtility] = []
    
    def start(self):
        self.table.start()

        for player in self.table.players:
            self.p.append(PlayerUtility(player, self.table))
    

