import enum
from game import *
from dataclasses import dataclass

class Package:
    class Package:
        pass

    @dataclass(init=True)
    class PlayCard(Package):
        hand :Hand

    @dataclass(init=True)
    class PrevHand(Package):
        hand: Hand

    @dataclass(init=True)
    class CardLeft(Package):
        cards_count: list[tuple[str,int]]

    @dataclass(init=True)
    class InitCard(Package):
        cards: list

    @dataclass(init=True)
    class GameOver(Package):
        winner: str

    @dataclass(init=True)
    class YourTurn(Package):
        force: bool

    @dataclass(init=True)
    class ChangeTurn(Package):
        name: str

    @dataclass(init=True)
    class ChkValid(Package):
        hands: list[Hand]

    @dataclass(init=True)
    class ResValid(Package):
        replies: list[tuple[Hand, bool, str]] # Hand is_valid not_valid_reason

    @dataclass(init=True)
    class SendName(Package):
        name: str

    @dataclass(init=True)
    class GetPlayer(Package):
        players: list[str]