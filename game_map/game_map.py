import numpy as np
from tcod.console import Console

import tile_types
from game_map.areas.area import Area
from game_map.direction.direction import Direction
from game_map.rooms.rooms import LRoom, Room


class GameMap(Area):
    def __init__(self, h: int, w: int):
        super().__init__(h, w)
        self.tiles = np.full((h, w), fill_value=tile_types.wall)

    def render(self, console: Console) -> None:
        console.rgb[0 : self.h, 0 : self.w] = self.tiles["dark"]


class Wall(Area):
    def __init__(self, h: int, w: int):
        super().__init__(h, w)
        self.tiles = np.full((h, w), fill_value=tile_types.wall)
        self.object_area = np.full((h, w), fill_value=False)
        np.fill_diagonal(self.object_area, True)


def generate_dungeon(map_height, map_width) -> GameMap:
    game_map = GameMap(map_height, map_width)

    room1 = LRoom(40, 60, Direction.WEST)
    room1.fill_border(tile_types.test2)
    room2 = Room(20, 20)
    room2.fill_border(tile_types.test1)

    room3 = LRoom(10, 10)
    room3.fill_border(tile_types.test2)

    y, x = room2.fit_in_touching_border(room3, Direction.EAST)
    if y:
        room2.place_in(y, x, room3)

    y, x = room1.fit_in_touching_border(room2, Direction.NORTH)
    if y:
        room1.place_in(y, x, room2)

    y, x = 1, 1
    if game_map.set_in_bbox(y, x, room1):
        game_map.place_in(y, x, room1)
    return game_map
