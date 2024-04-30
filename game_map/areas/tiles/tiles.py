"""Set class."""

from __future__ import annotations

from copy import deepcopy
from typing import Tuple, List

import numpy as np
from numpy.typing import NDArray
from tcod.console import Console

import tile_types
from game_map.areas.tiles.supplementaries import Point
from game_map.direction.connectivity import Connectivity
from game_map.direction.direction import Direction

from utils.utils import add_tuples, subtract_tuples


class Tiles:
    """Represents an array of tiles."""

    def __init__(
        self, size: Tuple, fill_value=tile_types.floor, empty: bool = False
    ) -> None:
        self._tiles = np.full(size, fill_value=fill_value)
        if empty:
            self._tiles["mask"] = False

    @property
    def size(self):
        return self._tiles.shape

    @property
    def h(self):
        return self._tiles.shape[0]

    @property
    def w(self):
        return self._tiles.shape[1]

    @property
    def mask(self):
        return self._tiles["mask"]

    @property
    def placable(self):
        return self._tiles["placeable"]

    @property
    def walkable(self):
        return self._tiles["walkable"]

    @mask.setter
    def mask(self, mask):
        self._tiles["mask"] = mask
        self._tiles["placeable"] &= self._tiles["mask"]

    @property
    def tiles(self):
        return self._tiles

    def __sub__(self, other: Tiles) -> Tiles:
        if not self.same_size(other):
            raise ValueError("Operation with tiles of different sizes.")
        result = deepcopy(self)
        result._tiles["mask"] = self.mask & ~other.mask
        result.tighten()
        return result

    def __isub__(self, other: Tiles) -> Tiles:
        if not self.same_size(other):
            raise ValueError("Operation with tiles of different sizes.")
        self._tiles["mask"] = self.mask & ~other.mask
        # self.tighten()
        return self

    def __add__(self, other: Tiles) -> Tiles:
        if not self.same_size(other):
            raise ValueError("Operation with tiles of different sizes.")
        result = deepcopy(self)
        result._tiles[other.mask] = other._tiles
        return result

    def __iadd__(self, other: Tiles) -> Tiles:
        if not self.same_size(other):
            raise ValueError("Operation with tiles of different sizes.")
        self._tiles[other.mask] = other._tiles
        return self

    def __neg__(self):
        result = deepcopy(self)
        result._tiles["mask"] = ~self.mask
        return result

    def set_unplaceable(self, p: Point, other: tiles):
        self.tiles["placeable"][p.y : p.y + other.h, p.x : p.x + other.w] = (
            self.tiles["placeable"][p.y : p.y + other.h, p.x : p.x + other.w]
            & ~other.mask
        )

    def point_in_bbox(
        self,
        p: Point,
    ) -> bool:
        """Checks whether a point is inside the bounding box of the tiles."""
        return 0 <= p.y < self.h and 0 <= p.x < self.w

    def is_subset(self, p: Point, other: Tiles) -> bool:
        if not self.set_in_bbox(p, other):
            return False
        return np.all(~other.mask | self.mask[p.y : p.y + other.h, p.x : p.x + other.w])

    def is_placable(self, p: Point, other: Tiles) -> bool:
        if not self.set_in_bbox(p, other):
            return False
        return np.all(
            ~other.mask | self.placable[p.y : p.y + other.h, p.x : p.x + other.w]
        )

    def collides(self, p: Point, other: Tiles) -> bool:
        return np.all(
            other.clipped(p, self.size).mask
            & self.mask[max(0, p.y) : p.y + other.h, max(0, p.x) : p.x + other.w]
        )

    def same_size(self, other: Tiles) -> bool:
        return self.size == other.size

    def clear_mask(self) -> None:
        self.mask.fill(False)

    def frontier_in_direction(self, direction: Direction) -> Tiles:
        """Returns a tile object that borders with background in the direction."""
        moved = self.moved_mask(direction.get_opposite())
        frontier = deepcopy(self)
        frontier -= moved
        return frontier

    def get_mask_indexes(self) -> NDArray[np.int32]:
        """Returns mask indexes of the object in shape (2,<object_size>)."""
        return np.transpose(np.nonzero(self.mask))

    def set_mask_indexes(self, indexes: NDArray[np.int32]) -> None:
        indexes = np.transpose(indexes)
        self.mask[indexes[0], indexes[1]] = True

    def clip_indexes(self, indexes: NDArray[np.int32]) -> NDArray[np.int32]:
        """Returns indexes with those out of bounds removed."""
        return indexes[
            (0 <= indexes[:, 0])
            & (0 <= indexes[:, 1])
            & (indexes[:, 0] < self.h)
            & (indexes[:, 1] < self.w)
        ]

    def clipped(self, p: Point, size: Tuple) -> (Tiles, Point):
        """Returns a clipped tiles as if it was put in another tiles of specific size in
        the specific position."""
        yl = abs(min(0, p.y))
        yr = min(size[0] - p.y, self.h)
        xl = abs(min(0, p.x))
        xr = min(size[1] - p.x, self.w)

        if xl > xr or yl > yr:
            return Tiles((0, 0)), Point(0, 0)

        clipped = Tiles((yr - yl, xr - xl), empty=True)
        clipped._tiles = deepcopy(self._tiles[yl:yr, xl:xr])
        return clipped, Point(max(0, p.y), max(0, p.x))

    def moved_mask(self, direction: Direction, offset: int = 1) -> Tiles:
        moved = Tiles(self.size, empty=True)
        if offset == 0:
            moved._tiles["mask"] = self.mask
            return moved
        object_indexes = self.get_mask_indexes()
        moved_indexes = object_indexes + direction.coordinates() * offset
        moved_indexes = self.clip_indexes(moved_indexes)
        moved.set_mask_indexes(moved_indexes)
        return moved

    def flip(self) -> None:
        self._tiles = np.flip(self._tiles)

    def fill(self, fill_value) -> None:
        self._tiles = np.full(self.size, fill_value=fill_value)

    def inner_border(self, connectivity: Connectivity = Connectivity.EIGHT) -> Tiles:
        """Returns the inner border of the mask. A border tile is the one connected to
        background."""
        kernel = connectivity.get_adjacency_mask()
        border = deepcopy(self)
        border.clear_mask()
        for i in np.ndindex(self.size):
            if not self.mask[i]:
                continue
            for k in kernel:
                n = add_tuples(i, k)
                if not self.point_in_bbox(Point(n[0], n[1])) or not self.mask[n]:
                    border.mask[i] = True
                    break
        return border

    def corners(self, direction: Direction) -> Tiles:
        """Returns corners of the set in a given direction. The direction and its
        clockwise neighbour specifies the corner orientation."""
        from game_map.areas.tiles.morphology.operations import hit_or_miss
        from game_map.areas.tiles.morphology.structural_element import corner_se

        result = Tiles(self.size)
        result.mask = hit_or_miss(self.placable, corner_se(direction))
        return result

    def tighten(self):
        """Tightens the bounding box around the object area."""
        raise NotImplementedError

    def set_in_bbox(self, p: Point, set: Tiles) -> bool:
        """Checks whether a whole tiles is inside the bounding box of the
        tiles."""
        return self.point_in_bbox(p) and self.point_in_bbox(
            Point(p.y + set.h - 1, p.x + set.w - 1)
        )

    def merge_mask(self, p: Point, other: Tiles) -> None:
        """Performs a union of two tiles at the given position."""
        mask_copy = deepcopy(self.mask)
        mask_copy[p.y : p.y + other.h, p.x : p.x + other.w] = other.mask
        self.mask = mask_copy

    def merge(self, p: Point, other: Tiles) -> None:
        """Performs a union of two tiles at the given position."""
        self._tiles[p.y : p.y + other.h, p.x : p.x + other.w][other.mask] = (
            other._tiles[other.mask]
        )

    def merger(self, p: Point, other: Tiles) -> Tiles:
        """Returns a union of two tiles."""
        union = deepcopy(self)
        union.merge(p, other)
        return union

    def subtract_mask(self, p: Point, other: Tiles) -> None:
        """Subtracts two tiles at the given position."""
        mask_copy = deepcopy(self.mask)
        mask_copy[p.y : p.y + other.h, p.x : p.x + other.w] = (
            mask_copy[p.y : p.y + other.h, p.x : p.x + other.w] & ~other.mask
        )
        self.mask = mask_copy

    def mask_subtraction(self, p: Point, other: Tiles) -> Tiles:
        difference = deepcopy(self)
        difference.subtract_mask(p, other)
        return difference

    def intersect_mask(self, p: Point, other: Tiles) -> None:
        """Performs an intersection of two tiles at the given position."""
        cutout = self.mask[p.y : p.y + other.h, p.x : p.x + other.w].copy()
        self.clear_mask()
        self.mask[p.y : p.y + other.h, p.x : p.x + other.w] = cutout & other.mask

    def mask_intersection(self, p: Point, other: Tiles) -> Tiles:
        """Returns an intersection of two tiles."""
        intersection = deepcopy(self)
        intersection.intersect_mask(p, other)
        return intersection

    def render(self, console: Console, origin: Point):
        console.rgb[
            origin.y : origin.y + self.h,
            origin.x : origin.x + self.w,
        ][
            self.mask
        ] = self._tiles["dark"][self.mask]

    def fit_in(self, to_fit: Tiles) -> List[Point]:
        valid_points = []
        mask_indexes = self.get_mask_indexes()
        for i in mask_indexes:
            origin = Point.from_tuple(i)
            if self.is_placable(origin, to_fit):
                valid_points.append(origin)
        return valid_points

    def fit_in_direction(
        self,
        to_fit: Tiles,
        anchor: Tiles,
        directions: Tuple = Direction.get_all_directions(),
    ) -> List[Point]:
        valid_points = []
        anchor_touch_indexes = anchor.get_mask_indexes()
        for direction in directions:
            set_touch_indexes = to_fit.frontier_in_direction(
                direction.get_opposite()
            ).get_mask_indexes()
            for i in anchor_touch_indexes:
                for j in set_touch_indexes:
                    origin = Point(*subtract_tuples(i, j))
                    if not self.is_placable(origin, to_fit):
                        continue
                    valid_points.append(origin)
        return valid_points

    def fit_in_touching(
        self, to_fit: Tiles, anchor: Tiles, direction: Direction, offset: int = 0
    ) -> List[Point] | None:
        """Fits in another tiles touching the anchor in the given direction. The new
        tiles will not collide with the anchor."""
        anchor_touch_set = anchor.moved_mask(direction, offset + 1)
        anchor_touch_set -= anchor.moved_mask(direction, offset)
        anchor_touch_indexes = anchor_touch_set.get_mask_indexes()

        set_touch_indexes = to_fit.frontier_in_direction(
            direction.get_opposite()
        ).get_mask_indexes()

        valid_points = []
        for i in anchor_touch_indexes:
            for j in set_touch_indexes:
                origin = Point(*subtract_tuples(i, j))
                if not self.is_placable(origin, to_fit):
                    continue
                if anchor.collides(origin, to_fit):
                    continue
                valid_points.append(origin)
        return valid_points
