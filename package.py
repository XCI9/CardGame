import enum
from utilities import *
from dataclasses import dataclass

class Package:
    class Package:
        hash: int

    @dataclass(init=True)
    class PlayCard(Package):
        id: int
        hand: Hand

    @dataclass(init=True)
    class PlayErase(Package):
        id: int
        card: int

    @dataclass(init=True)
    class SyncGame(Package):
        table: TableClassic
        id: int

    @dataclass(init=True)
    class GameOver(Package):
        winner: str

    @dataclass(init=True)
    class SendName(Package):
        name: str

    @dataclass(init=True)
    class GetPlayer(Package):
        players: list[str]
        full_count: int # the player count in current gamemode

    @dataclass(init=True)
    class AgainChk(Package):
        agree: bool

    @dataclass(init=True)
    class SyncReq(Package):
        pass