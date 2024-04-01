import numpy as np
from tcod.console import Console

import tile_types
from game_map.areas.area import Area
from game_map.areas.sets.set import Set
from game_map.areas.sets.supplementaries import Size, Point
from game_map.direction.direction import Direction
from game_map.rooms.rooms import LRoom, Room


class GameMap(Area):
    def __init__(self, size: Size):
        super().__init__(size)
        self.tiles = np.full(size.tuple(), fill_value=tile_types.wall)


# class Wall(Area):
#     def __init__(self, h: int, w: int):
#         super().__init__(h, w)
#         self.tiles = np.full((h, w), fill_value=tile_types.wall)
#         self.object_area = np.full((h, w), fill_value=False)
#         np.fill_diagonal(self.object_area, True)


def generate_dungeon(map_height, map_width) -> GameMap:
    game_map = GameMap(Size(map_height, map_width))

    room1 = LRoom(Size(40, 30), Direction.WEST)
    room1.fill_border(tile_types.test2)

    p = Point(5, 35)
    if game_map.set_in_bbox(p, room1):
        game_map.place_in(p, room1)

    room2 = LRoom(Size(20, 20), Direction.EAST)
    # room2.fill_border(tile_types.test1)

    frontier = room1.frontier_in_direction(Direction.WEST)

    frontier.transform(p, game_map.size)

    g = game_map.difference(p, room1) + frontier

    pp = g.fit_in(room2, frontier, (Direction.WEST,))

    game_map.place_in_randomly(pp, room2)

    return game_map
