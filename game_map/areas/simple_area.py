from __future__ import annotations

from copy import deepcopy
from typing import Tuple

import numpy as np

from game_map.areas.tiles.supplementaries import Point
from game_map.areas.tiles.tiles import Tiles


class SimpleArea:
    def __init__(self, size: Tuple, origin: Point = Point(0, 0)):
        self.parent = None
        self.origin = origin
        self.tiles = Tiles(size)

    @staticmethod
    def create_from_tiles(in_tiles: Tiles) -> SimpleArea:
        result = SimpleArea(in_tiles.size)
        result.tiles = in_tiles
        return result

    @property
    def size(self):
        return self.tiles.size

    @property
    def h(self):
        return self.tiles.h

    @property
    def w(self):
        return self.tiles.w

    def fill(self, fill_value) -> None:
        """Fills the tiles with a value through the whole bounding box."""
        self.tiles.fill(fill_value)

    def fill_border(self, fill_value) -> None:
        """Sets border the border to have specific value."""
        border_mask = self.tiles.inner_border().mask
        self.tiles.tiles[border_mask] = fill_value

    def fill_in(self, area: SimpleArea) -> None:
        """Fills the tiles with s value in areas defined by the given tiles."""
        self.tiles.merge(area.origin, area.tiles)

    def fill_out(self, area: SimpleArea) -> None:
        self.tiles.subtract_mask(area.origin, area.tiles)

    def stretch(self) -> None:
        """Transforms the set as if it was inside a set of certain size on a certain
        position."""
        stretched_tiles = Tiles(self.parent.size, empty=True)
        stretched_tiles.merge(self.origin, self.tiles)
        self.origin = Point(0, 0)
        self.tiles = stretched_tiles

    def stretched(self) -> SimpleArea:
        """Returns the set as if it was inside a set of certain size of a certain
        position."""
        stretched = deepcopy(self)
        stretched.stretch()
        return stretched

    def inner_border(self):
        return SimpleArea.create_from_tiles(self.tiles.inner_border())

    def set_unplaceable(self, area: SimpleArea):
        self.tiles.set_unplaceable(area.origin, area.tiles)

    def is_inside(self, p: Point) -> bool:
        return self.tiles.point_in_bbox(p)

    def volume(self) -> int:
        return np.count_nonzero(self.tiles.mask)

    def density(self) -> float:
        return (self.volume() - np.count_nonzero(self.tiles.placable)) / self.volume()
