from typing import Tuple


import tile_types
from game_map.areas.area import Area
from game_map.areas.tiles.supplementaries import Point
from game_map.direction.direction import Direction
from game_map.areas.rooms.rooms import LRoom


class GameMap(Area):
    def __init__(self, size: Tuple):
        super().__init__(size)
        self.fill(tile_types.wall)


def generate_dungeon(map_height, map_width) -> GameMap:

    # TEST AREA

    game_map = GameMap((map_height, map_width))

    room1 = LRoom((40, 30), Direction.EAST)
    room1.origin = Point(1, 40)

    game_map.place_in(room1)

    room2 = LRoom((20, 20), Direction.WEST)

    p = game_map.fit_next_to(room2, room1, Direction.WEST)

    game_map.place_in_randomly(p, room2)

    return game_map
