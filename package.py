import enum
from game import *
from dataclasses import dataclass

class Package:
    @dataclass(init=True)
    class PlayCard:
        hand :Hand

    @dataclass(init=True)
    class PrevHand:
        hand: Hand

    @dataclass(init=True)
    class CardLeft:
        cards_count: list[tuple[str,int]]

    @dataclass(init=True)
    class InitCard:
        cards: list

    @dataclass(init=True)
    class GameOver:
        winner: str

    @dataclass(init=True)
    class YourTurn:
        force: bool

    @dataclass(init=True)
    class ChangeTurn:
        name: str

    @dataclass(init=True)
    class ChkValid:
        hands: list[Hand]

    @dataclass(init=True)
    class ResValid:
        replies: list[tuple[Hand, bool, str]]

    @dataclass(init=True)
    class SendName:
        name: str