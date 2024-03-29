import random

import numpy as np

import tile_types
from direction import Direction, Orientation
from set import Set


def from_set(set, fill_value):
    area = Area(set.h, set.w)
    area.object_mask = set.object_mask
    area.fill_self(fill_value=fill_value)
    return area


class Area(Set):
    def __init__(self, h: int, w: int, empty: bool = False):
        super().__init__(h, w, empty)
        self.parent = None
        self.children = []
        self.tiles = np.full((h, w), fill_value=tile_types.void)

    def fill_border(self, fill_value):
        border = from_set(self.get_inner_border("8"), fill_value)
        self.place_in(0, 0, border)

    def fill_in(self, y, x, set, fill_value):
        self.tiles[y: y + set.h, x: x + set.w] = np.where(set.object_mask,
                                                          fill_value,
                                                          self.tiles[
                                                          y: y + set.h,
                                                          x: x + set.w], )

    def fill_self(self, fill_value, offset: int = 0):
        self.tiles[offset: self.h - offset, offset: self.w - offset] = np.full(
            (self.h - 2 * offset, self.w - 2 * offset), fill_value=fill_value)

    def place_in(self, y, x, area):
        if not self.point_is_in_bbox(y, x) or not self.point_is_in_bbox(
                y + area.h - 1, x + area.w - 1):
            raise ValueError("Area to insert does not fit inside the parent.")
        self.children.append(area)
        self.tiles[y: y + area.h, x: x + area.w] = np.where(area.object_mask,
                                                            area.tiles,
                                                            self.tiles[
                                                            y: y + area.h,
                                                            x: x + area.w], )

    def fit_in_touching_wall(self, set, direction: Direction,
                             corner_offset: int = 0, wall_offset: int = 0, ):
        if direction.get_orientation() == Orientation.HORIZONTAL:
            x = random.randrange(corner_offset, self.w - set.w - corner_offset)

            if direction == Direction.WEST:
                y = wall_offset
            else:
                y = self.h - set.h - wall_offset
        else:
            y = random.randrange(corner_offset, self.h - set.h - corner_offset)

            if direction == Direction.NORTH:
                x = wall_offset
            else:
                x = self.w - set.w - wall_offset
        if self.set_is_in_bbox(y, x, set):
            return y, x
        return None, None

    def fit_in_touching_corner(self, set, direction: Direction,
                               wall_offset: int = 0):
        """Places an area in the corner. The area will be touching the wall
        in defined direction and the next wall clockwise of that direction.
        For example: if direction is NORTH then the area will be touching
        NORTH and EAST walls."""
        if direction == Direction.NORTH:
            y = wall_offset
            x = self.w - set.w - wall_offset
        elif direction == Direction.EAST:
            y = self.h - set.h - wall_offset
            x = self.w - set.w - wall_offset
        elif direction == Direction.SOUTH:
            y = self.h - set.h - wall_offset
            x = wall_offset
        else:
            y = wall_offset
            x = wall_offset
        if self.set_is_in_bbox(y, x, set):
            return y, x
        return None, None
