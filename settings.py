import json


SETTINGS: dict = json.load(open("settings.json"))
N_MINES: int = SETTINGS["mines"]
TILE_SIZE: int = SETTINGS["tile-size"]
WIDTH: int = SETTINGS["width"]
HEIGHT: int = SETTINGS["height"]
DISPLAY_W: int = WIDTH * TILE_SIZE
DISPLAY_H: int = HEIGHT * TILE_SIZE
TFPS: float = SETTINGS["fps"]
XOFFSET: int = SETTINGS["numbers-x-offset"]
YOFFSET: int = SETTINGS["numbers-y-offset"]
FONT_PATH: str = SETTINGS["font-path"]
MINE_PATH: str = SETTINGS["mine-path"]
FLAG_PATH: str = SETTINGS["flag-path"]
ANIMATION_PATH: str = SETTINGS["animation-path"]
ANIMATION_PATH.strip("/\\")
ANIMATION_SPEED: float = SETTINGS["explode-animation-speed"]
STATUS_BAR_HEIGHT = 100

HIDDEN_TILE_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["hidden"])
MARKED_TILE_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["marked"])
NUMBER_BG_TILE_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["number-bg"])
NUMBER_FG_TILE_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["number-fg"])
EMPTY_TILE_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["empty"])
WIN_MES_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["win-message"])
MINES_STATUS_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["mines-remaining"])
STATUS_BAR_BG_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["status-bar-bg"])