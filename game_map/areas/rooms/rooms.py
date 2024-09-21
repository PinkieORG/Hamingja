import random
from typing import Tuple

import tile_types
from game_map.areas.area import Area
from game_map.areas.prototype_areas.prototype_areas import (
    create_carpet,
    create_column,
)
from game_map.areas.random_simple_areas import (
    DimensionRange,
    random_rectangle_area,
)
from game_map.areas.tiles.supplementaries import Point
from game_map.direction.direction import Direction


# def generate_multi_room(width: int, height: int, subroom_dim_range:
#    DimensionRange):


def prototype_room(size: Tuple):
    room = LRoom(size)
    carpet_size = DimensionRange(
        room.h // 4,
        room.h // 3,
        room.w // 4,
        room.w // 3,
    ).sample()
    carpet = create_carpet(carpet_size)
    p = room.fit_in_corner(carpet)
    room.place_in_randomly(p, carpet)
    room.fill_border(tile_types.wall)
    for i in range(3):
        column = create_column()
        p = room.fit_in_touching_border(column, Direction.WEST, 1)
        room.place_in_randomly(p, column)
    for i in range(3):
        column = create_column()
        p = room.fit_in_touching_border(column, Direction.NORTH, 1)
        room.place_in_randomly(p, column)
    return room


class Room(Area):
    def __init__(self, size: Tuple):
        super().__init__(size)
        self.fill(tile_types.floor)
        if __debug__:
            self.fill_border(tile_types.border_debug)
        else:
            self.fill_border(tile_types.wall)

    @staticmethod
    def from_dim_range(dim_range: DimensionRange):
        h = random.randrange(dim_range.min_w, dim_range.max_w + 1)
        w = random.randrange(dim_range.min_h, dim_range.max_h + 1)
        return Room((h, w))

    def make_entrance(self, position: Point) -> None:
        entrance = Area((1, 1), position)
        self.place_in(entrance)


# class MultiRoom(Room):
#     def __init__(self, h: int, w: int):
#         super().__init__(h, w)
#         self.fill(tile_types.wall)
#         starting_direction = Direction.get_random_direction()
#         dim_range = DimensionRange(
#             7,
#             18,
#             7,
#             18,
#         )
#         start_room = Room.from_dim_range(dim_range)
#         y, x = self.fit_in_touching_border(start_room, starting_direction)
#         self.place_in(y, x, start_room)
#         self.active_border = self.inner_border("4") - start_room.inner_border("4")
#
#     def place_room(self):
#         pass


class LRoom(Room):
    def __init__(self, size: Tuple, direction: Direction = None):
        if direction is None:
            direction = Direction.get_random_direction()
        super().__init__(size)
        fill_dim_range = DimensionRange(
            self.h // 2.5,
            self.h // 1.5,
            self.w // 2.5,
            self.w // 1.5,
        )
        rectangle = random_rectangle_area(fill_dim_range)
        p = self.fit_in_corner(rectangle, (direction,))[0]
        rectangle.origin = p
        self.fill_out(rectangle)
        if __debug__:
            self.fill_border(tile_types.border_debug)
        else:
            self.fill_border(tile_types.wall)
        self.set_unplaceable(self.inner_border())


# class MultiRectangleRoom(Room):
#     def __init__(self, h: int, w: int):
#         super().__init__(h, w)
#         self.object_area = np.full((h, w), fill_value=False)
#         for direction in Direction:
#             wall_rectangle = self.get_wall_rectangle()
#             y, x = self.fit_in_touching_border(wall_rectangle, direction, 2)
#             self.unify(y, x, wall_rectangle)
#         self.fill_self(tile_types.floor)
#         self.fill_border(tile_types.object)
#
#     def get_wall_rectangle(self):
#         dim_range = DimensionRange(
#             self.h // 3,
#             self.h // 1.5,
#             self.w // 3,
#             self.w // 1.5,
#         )
#         return RandomRectangleSet(dim_range)
#
#     def place_rectangle_touching_wall(self, direction: Direction):
#         dim_range = DimensionRange(
#             self.h // 4,
#             self.h // 2,
#             self.w // 4,
#             self.w // 2,
#         )
#         rectangle = RandomRectangle(dim_range, tile_types.object)
#         self.fit_in_touching_border(rectangle, direction)
