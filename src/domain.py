from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Set


class TileState(Enum):
    TBD = auto()
    GREY = auto()
    GREEN = auto()
    YELLOW = auto()

    def get(s: str) -> "TileState":
        _map = {
            "present": TileState.YELLOW,
            "correct": TileState.GREEN,
            "absent": TileState.GREY
        }
        if s in _map:
            return _map[s]
        return TileState.TBD


@dataclass
class Tile:
    state: TileState
    value: str


class GameState:
    def __init__(self, rows: List[List[Tile]]) -> None:
        self.correct: Dict[int, str] = dict()
        self.max_len: Dict[str, int] = dict()
        self.wrong_pos: Dict[int, Set[str]] = dict()
        self.characters_seen: Dict[str, int] = dict()

        for row in rows:
            if not self.parse_row(row):
                break

    def parse_row(self, row: List[Tile]) -> bool:
        for i, tile in enumerate(row):
            if tile.state == TileState.GREEN:
                self.correct[i] = tile.value
                self.add_character(tile.value)
            elif tile.state == TileState.YELLOW:
                if i in self.wrong_pos:
                    self.wrong_pos[i].add(tile.value)
                else:
                    self.wrong_pos[i] = {tile.value}
                self.add_character(tile.value)
            elif tile.state == TileState.GREY:
                self.max_len[tile.value] = self.characters_seen.setdefault(tile.value, 0)
            else:
                return False
        return True

    def add_character(self, ch: str) -> None:
        if ch in self.characters_seen:
            self.characters_seen[ch] += 1
        else:
            self.characters_seen[ch] = 1
