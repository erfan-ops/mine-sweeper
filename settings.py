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
ANIMATION_SPEED: int = SETTINGS["explode-animation-speed"]
STATUS_BAR_HEIGHT = 100