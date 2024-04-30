from __future__ import annotations

from copy import deepcopy
from typing import Tuple, List

import numpy as np

from game_map.areas.tiles.supplementaries import Point
from game_map.areas.tiles.tiles import Tiles
from game_map.direction.direction import Direction


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
        """Fills the tiles with a value in the given area."""
        self.tiles.merge(area.origin, area.tiles)

    def fill_out(self, area: SimpleArea) -> None:
        """Sets the tiles to not belongs to the object."""
        self.tiles.subtract_mask(area.origin, area.tiles)

    def filled_out(self, area: SimpleArea) -> SimpleArea:
        """Returns an area which is missing the tiles of the given area from its
        mask."""
        filled_out = deepcopy(self)
        filled_out.fill_out(area)
        return filled_out

    def stretch(self, size: Tuple) -> None:
        """Transforms the set as if it was inside a set of certain size on a certain
        position."""
        stretched_tiles = Tiles(size, empty=True)
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
        """Returns the inner border of the area."""
        return SimpleArea.create_from_tiles(self.tiles.inner_border())

    def set_unplaceable(self, area: SimpleArea):
        self.tiles.set_unplaceable(area.origin, area.tiles)

    def is_inside(self, p: Point) -> bool:
        """Checks if the point is inside the bounding box."""
        return self.tiles.point_in_bbox(p)

    def volume(self) -> int:
        """Returns the number of pixels of the mask."""
        return np.count_nonzero(self.tiles.mask)

    def density(self) -> float:
        """Returns the ratio of placable tiles to all the tiles."""
        return (self.volume() - np.count_nonzero(self.tiles.placable)) / self.volume()

    def uncover(self):
        return self.filled_out(self.inner_border())

    def fit_in(self, to_fit: SimpleArea) -> List[Point]:
        return self.tiles.fit_in(to_fit.tiles)

    def fit_in_direction(
        self,
        to_fit: SimpleArea,
        anchor: SimpleArea,
        directions: Tuple = Direction.get_all_directions(),
    ) -> List[Point]:
        """Fits in another area on the points specified by the anchor in specific
        direction."""
        return self.tiles.fit_in_direction(
            to_fit.tiles, anchor.stretched().tiles, directions
        )

    def fit_in_touching(
        self,
        to_fit: SimpleArea,
        anchor: SimpleArea,
        direction: Direction,
        offset: int = 0,
    ) -> List[Point]:
        """Fits in another area touching the anchor in the given direction. The new
        tiles will not collide with the anchor."""
        return self.tiles.fit_in_touching(
            to_fit.tiles, anchor.stretched().tiles, direction, offset
        )

    def fit_in_touching_border(
        self,
        to_fit: SimpleArea,
        direction: Direction,
        border_offset: int = 0,
    ) -> List[Point]:
        """Fits in another area touching the inner border with"""
        return self.tiles.fit_in_touching(
            to_fit.tiles, self.tiles.inner_border(), direction, border_offset
        )

    def fit_in_corner(
        self, to_fit: SimpleArea, directions: Tuple = Direction.get_all_directions()
    ) -> List[Point]:
        """Places an areas in the corner. The areas will be touching the wall
        in defined direction and the next wall clockwise of that direction.
        For example: if direction is NORTH then the areas will be touching
        NORTH and EAST walls."""
        result = []
        for direction in directions:
            result += self.tiles.fit_in_direction(
                to_fit.tiles, self.tiles.corners(direction), (direction.get_opposite(),)
            )
        return result
