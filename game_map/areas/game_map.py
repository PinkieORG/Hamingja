from typing import Tuple


import tile_types
from game_map.areas.area import Area


class GameMap(Area):
    def __init__(self, size: Tuple):
        super().__init__(size)
        self.fill(tile_types.wall)
