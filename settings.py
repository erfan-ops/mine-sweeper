import json


SETTINGS: dict = json.load(open("settings.json"))
N_MINES: int = SETTINGS["mines"]
TILE_SIZE: int = SETTINGS["tile-size"]
WIDTH: int = SETTINGS["width"]
HEIGHT: int = SETTINGS["height"]
STATUS_BAR_HEIGHT = 100
DISPLAY_W: int = WIDTH * TILE_SIZE
GAME_CANVAS_DISPLAY_H: int = HEIGHT * TILE_SIZE
DISPLAY_H: int = GAME_CANVAS_DISPLAY_H + STATUS_BAR_HEIGHT
ASPECT_RATIO = (1, GAME_CANVAS_DISPLAY_H/DISPLAY_W)
ZOOM_LIMIT = DISPLAY_W / ASPECT_RATIO[0] - 1
TFPS: float = SETTINGS["fps"]
XOFFSET: int = SETTINGS["numbers-x-offset"]
YOFFSET: int = SETTINGS["numbers-y-offset"]
FONT_PATH: str = SETTINGS["font-path"]
MINE_PATH: str = SETTINGS["mine-path"]
FLAG_PATH: str = SETTINGS["flag-path"]
ANIMATION_PATH: str = SETTINGS["animation-path"]
ANIMATION_PATH = ANIMATION_PATH.strip("/\\")
ANIMATION_SPEED: float = SETTINGS["explode-animation-speed"]

ZOOM_MULTPLIER: float = SETTINGS["zoom-multiplier"]

HIDDEN_TILE_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["hidden"])
MARKED_TILE_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["marked"])
NUMBER_BG_TILE_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["number-bg"])
NUMBER_FG_TILE_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["number-fg"])
EMPTY_TILE_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["empty"])
WIN_MES_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["win-message"])
MINES_STATUS_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["mines-remaining"])
TIMER_STATUS_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["timer"])
STATUS_BAR_BG_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["status-bar-bg"])
MINE_BG_COLOR: tuple[int, int, int] = tuple(SETTINGS["colors"]["mine-bg"])

DO_SMART_CLICK: bool = SETTINGS["smart-click"]