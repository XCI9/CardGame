# -*- coding: UTF-8 -*-
"""Utilities for the game of card31.

Global variable
----------
hand_ranking : dict
    A dictionary that returns the rank of a hand pattern.

Functions
----------
evaluate_cards -- Evaluate all available hands that can be made.
ind_higher_ranking -- compaire the rank of two hands.

Classes
----------
Hand -- The class instance contains cards, rank, value and suit of a hand.
TableClassic -- A game table for player to play a game with classic game mode.
"""

from collections import Counter
from dataclasses import dataclass
from typing import Literal
import random
__all__ = [
    'hand_ranking',
    'evaluate_cards',
    'ind_higher_ranking',
    'Hand',
    'TableClassic',
    'Player'
]

@dataclass(init=True)
class Hand():
    """The class instance contains cards, rank, value and suit of a hand."""
    card: tuple
    rank: str = 'None'
    value: int = -1
    suit: int = -1
    eraseable: bool = False

    def __gt__(self, other) -> bool:
        if ind_higher_ranking(self, other) == 1:
            return True
        elif ind_higher_ranking(self, other) == 2:
            return False
        else: # equal rank
            if self.value > other.value:
                return True 
            elif self.value < other.value:
                return False
            else: # equal value
                if self.suit > other.suit:
                    return True
                elif self.value < other.value:
                    return False
                else:
                    return False
    def __eq__(self, other) -> bool:
        if (ind_higher_ranking(self, other) == 0 and
            self.value == other.value and
            self.suit == other.suit):
            return True
        else:
            return False
    def __lt__(self, other) -> bool:
        return not (self.__eq__(other) or self.__gt__(other))
    def __le__(self, other):
        return (self.__eq__(other) or self.__lt__(other))
    def __ge__(self, other):
        return (self.__eq__(other) or self.__gt__(other))
    def __len__(self) -> bool:
        return len(self.card)

# First element has highest rank, last one has lowest rank.
# Then store it as dictionary to achieve O(1) access.
hand_ranking_table = (
    'void3',
    'rare triple',
    'triangle',
    'straight',
    'triple',
    'void2',
    'rare double',
    'squre',
    'double',
    'rare single',
    'single',
    'None'
)
hand_ranking = {}
for i in range(len(hand_ranking_table)):
    hand_ranking[hand_ranking_table[i]] = i + 1
del hand_ranking_table, i

def ind_higher_ranking(hand1: Hand, hand2: Hand) -> Literal[0, 1, 2]:
    """compaire the rank of two hands.

    Returns
    ----------
    index : int
        1 for hand1 has higher ranking, 
        2 for hand2 has higher ranking,
        0 for two hands have equal ranking.
    """
    rank1 = hand_ranking[hand1.rank]
    rank2 = hand_ranking[hand2.rank]
    if rank1 < rank2: result = 1
    if rank1 > rank2: result = 2
    if rank1 == rank2: result = 0
    return result


def evaluate_cards(cards: tuple[int] | list[int],
                   reprc_left: list[int] = []) -> list[Hand]:
    """Evaluate all available hands that can be made.

    Argument
    ----------
    cards : tuple
        The playing card.
    reprc_count : list[int], optinal
        reprc_left[N] contains the number of remaining unplayed
        representative cards. used for game rule 'rare'.
        (NOT YET DEVELOP, IT HAS NO EFFECT NOW)

    Returns
    ----------
    avaliable : list[Hand]
        A list that contains all avaliable hands.
    """
    # find representative card
    _reprc = []
    cards = list(cards)
    for card in cards:
        if not card // 10 == 0:
            _reprc.append(card // 10)
        _reprc.append(card % 10)
    _reprc.sort()
    cards.sort()

    avaliable = []
    if len(cards) == 3:
        ####  triangle  ####
        if cards[0]**2 + cards[1]**2 == cards[2]**2:
            rank = 'triangle'
            value = sum(_reprc)
            suit = -1
            avaliable.append( Hand(cards, rank, value, suit) )
        ####  straight  ####
        if cards[2] - cards[1] == 1 and cards[1] - cards[0] == 1:
            rank = 'straight'
            value = sum([max(int(digit) for digit in str(card)) for card in cards])
            suit = -1
            avaliable.append( Hand(cards, rank, value, suit) )
        ####  triple  ####
        dup = [(item, count) for item, count in
               Counter(_reprc).items() if count > 2 ]
        if not len(dup) == 0 :
            dup.sort()
            dup.reverse()
            value = dup[0][0]
            _reprc.remove(value)
            _reprc.remove(value)
            _reprc.remove(value)
            suit = sum(_reprc)
            ####  rare triple  ####
            if value > 3:
                rank = 'rare triple'
                avaliable.append( Hand(cards, rank, value, suit) )
            ####  void3  ####
            elif value == 0:
                rank = 'void3'
                avaliable.append( Hand(cards, rank, value, suit) )
            ####  triple  ####
            else:
                rank = 'triple'
                avaliable.append( Hand(cards, rank, value, suit) )
    if len(cards) == 2:
        ####  square  ####
        if cards[0]**2 == cards[1]:
            rank = 'square'
            value = sum(_reprc)
            suit = -1
            avaliable.append( Hand(cards, rank, value, suit) )

        dup = [(item, count) for item, count in 
               Counter(_reprc).items() if count > 1 ]
        if not len(dup) == 0:
            dup.sort()
            dup.reverse()
            value = dup[0][0]
            _reprc.remove(value)
            _reprc.remove(value)
            suit = sum(_reprc)
            ####  void2  ####
            if value == 0:
                rank = 'void2'
                avaliable.append( Hand(cards, rank, value, suit) )
            ####  double  ####
            rank = 'double'
            avaliable.append( Hand(cards, rank, value, suit) )
    if len(cards) == 1:
        rank = 'single'
        if len(_reprc) == 1:
            value = _reprc[0]
            suit = -1
            avaliable.append( Hand(cards, rank, value, suit) )
        if len(_reprc) == 2:
            value = _reprc[0]
            suit = _reprc[1]
            avaliable.append( Hand(cards, rank, value, suit) )
            if _reprc[0] != _reprc[1]:
                value = _reprc[1]
                suit = _reprc[0]
                avaliable.append( Hand(cards, rank, value, suit) )
    for hand in avaliable:
        if (len(set(str(hand.value) + str(hand.suit))) == 1 and
            hand.suit != -1):
            hand.eraseable = True

    return avaliable

class Table:
    def __init__(self) -> None:
        pass
class Player: pass

class TableClassic(Table):
    """A game table for player to play a game with classic game mode.
    
    Instance variable
    ----------
    cards : list
        Cards on the table.
    players : list[Player]
        the players that joined the game
    turn : int
        n when it is n-th turn. 0 when game not started.
    previous_hand : Hand
        The previous played hand, defalut is: 
        Hand(card=(), rank='None', value=-1, suit=-1)
    rule9 : bool
        Game rule that allows [2 cards hand] > [1 card hand].
    rule19 : bool
        Game rule that allows [3 cards hand] > [2 cards hand].
    rule29 : bool
        Game rule that allows [3 cards hand] > [1 card hand].
    
    Public methods
    ----------
    join -- Make a player join this table, return False for join denied.
    start -- Start game.
    is_playable_hand -- Evaluate whether a hand is playable now.
    play_hand -- play a hand onto table. Update rule9's if matches.
    erase -- Play one card onto table without any side effect.
    get_player -- Get the player object.
    turn_forward -- Make turn forward. check whether active player wins.
    empty_previous_hand -- Make previous played hand empty.
    """
    def __init__(self) -> None:
        self.cards = []
        self.players: list[Player] = []
        self.previous_hand = Hand((), 'None', -1, -1)
        self.turn = 0
        self._token = 0
        self.rule9 = False
        self.rule19 = False
        self.rule29 = False
    def __repr__(self) -> str:
        string = ( "A table with cards:\n"
                 + str(self.cards) + '\n' 
                 + "previous hand : "
                 + self.previous_hand.__repr__() + '\n'
                 + f"rule 9/19/29 : {self.rule9}/{self.rule19}/{self.rule29}"
        )
        return string
    def join(self, player) -> bool:
        """Make a player join this table, return False for join denied."""
        if len(self.players) == 3:
            return False
        if player in self.players:
            return False
        self.players.append(player)
        return True

    def start(self) -> bool:
        "Start game."
        if len(self.players) != 3:
            return False
        # decide dealer
        dealer_ind = random.randint(0, 2)
        self.players[dealer_ind].cards.append(1)
        self.players[dealer_ind].lastplayed = True
        self.players[dealer_ind].his_turn = True
        # deal
        deck = list(range(2, 32))
        random.shuffle(deck)
        self.players[0].cards += deck[0:10]
        self.players[1].cards += deck[10:20]
        self.players[2].cards += deck[20:30]
        self.players[0].in_game = True
        self.players[1].in_game = True
        self.players[2].in_game = True
        self._token = dealer_ind
        self.turn = 1
        return True

    def is_playable_hand(self, newhand: Hand) -> tuple:
        """Evaluate whether a hand is playable now."""
        if len(self.cards) == 0 and 1 not in newhand.card:
            return False, "首家需要打出1"
        if self.previous_hand.rank == 'None':
            return True, ''
        if (len(self.previous_hand) == 1 and len(newhand) == 2):
            if self.rule9:
                return True, ''
            else:
                return False, "2壓1✘"
        if (len(self.previous_hand) == 2 and len(newhand) == 3):
            if self.rule19:
                return True, ''
            else:
                return False, "3壓2✘"
        if (len(self.previous_hand) == 1 and len(newhand) == 3):
            if self.rule29:
                return True, ''
            else:
                return False, "3壓1✘"

        if self.previous_hand.rank in ('triangle', 'straight', 'square'):
            if newhand >= self.previous_hand: return True, ''
        else:
            if newhand > self.previous_hand: return True, ''
        return False, "無法壓過場上的牌"
    
    def get_player(self, shift: int = 0) -> Player:
        """Get the player object.
        
        Argument
        ----------
        shift : int, optional (default is 0)
            +1 to return next active player.
            0 to return active player.
            -1 to return previous active player.
        """
        holder = self._token
        if shift == 0:
            return self.players[holder]
        if shift == +1:
            next_holder = (holder + 1) % 3
            if not self.players[next_holder].in_game:
                next_holder = (next_holder + 1) % 3
            return self.players[next_holder]
        if shift == -1:
            prev_holder = (3 + holder - 1) % 3
            if not self.players[prev_holder].in_game:
                prev_holder = (3 + prev_holder - 1) % 3
            return self.players[prev_holder]

    def turn_forward(self, played_hand: bool) -> None:
        """Make turn forward. check whether active player wins.
        
        Argument
        ----------
        played_hand : bool
            Input True when player plays a hand.
            Input False when player pass his trun.
        """
        active_player = self.get_player()
        next_active_player = self.get_player(+1)
        # check if active player wins
        if len(active_player.cards) == 0:
            active_player.in_game = False
        # turn forward to next player
        if played_hand:
            for player in self.players:
                player.lastplayed = False
            active_player.lastplayed = True
        active_player.his_turn = False
        next_active_player.his_turn = True
        if next_active_player.lastplayed:
            self.empty_previous_hand()
        # pass token to next player
        self.turn += 1 
        holder = self._token
        next_holder = (holder + 1) % 3
        if not self.players[next_holder].in_game:
            next_holder = (next_holder + 1) % 3
        self._token = next_holder

    def play_hand(self, newhand: Hand) -> None:
        """play a hand onto table. Update rule9's if matches."""
        self.previous_hand = newhand
        self.cards += list(newhand.card)
        has9 = any(card == 9 for card in newhand.card)
        has19 = any(card == 19 for card in newhand.card)
        has29 = any(card == 29 for card in newhand.card)
        has8 = any(card == 8 for card in newhand.card)
        has18 = any(card == 18 for card in newhand.card)
        has28 = any(card == 28 for card in newhand.card)
        if has9: self.rule9 = True
        if has19: self.rule19 = True
        if has29: self.rule29 = True
        if has8: self.rule9 = False
        if has18: self.rule19 = False
        if has28: self.rule29 = False

    def empty_previous_hand(self) -> None:
        """Make previous played hand empty."""
        self.previous_hand = Hand((), 'None', -1, -1)
    def erase(self, card: int) -> None:
        """Play one card onto table without any side effect."""
        self.cards += [card]


class Player:
    """A player in a table.

    Instance variables
    ----------
    name : string
        The name of player.
    table : Table
        The table this player joined.
    cards : list[int]
        The cards player has.
    selected_cards : list[int]
        The cards that plater selected.
    lastplayed : bool
        If all other players choose to pass their turn after a player 
        has played a hand, that player can play any hand on to the tabel
        and he is not allowed to pass the turn.
    his_turn : bool
        True when the game is in player's turn.
        False when the player is wait for other players.
    in_game : bool
        True when player is still in the game. If a player plays all of his cards
        ,he finishs his game, so it'll becomes Flase.
    """
    def __init__(self, name = 'None') -> None:
        self.name = name
        self.cards = []
        self.selected_cards = []
        self.lastplayed = False
        self.his_turn = False
        self.in_game = False

    def __repr__(self) -> str:
        string = ( 
            f'name : {self.name}\n'
            + f'his_turn : {self.his_turn}\n'
            + f'in_game : {self.in_game}\n'
            + f'lastplayed : {self.lastplayed}\n'
            + f'cards :\n{self.cards}\n'
            + f'selected_cards : {self.selected_cards}'
        )
        return string
    def remove_cards(self, cards):
        for card in cards:
            self.cards.remove(card)
