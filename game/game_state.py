from enum import Enum, auto


class GameState(Enum):
    TITLE = auto()
    INTRO = auto()
    PLAYING = auto()
    PAUSED = auto()
    INVENTORY = auto()
    MAP_VIEW = auto()
    DIALOG = auto()
    PUZZLE = auto()
    QUEST_LOG = auto()
    OUTRO = auto()
