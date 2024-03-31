"""Set class."""

from __future__ import annotations
import random
from copy import copy, deepcopy
from typing import Tuple

import numpy as np
from numpy.typing import NDArray
from dimensions import DimensionRange
from direction import Direction
from utils import (
    add_tuples,
    subtract_tuples,
    Connectivity,
)


class Set:
    """Simple binary set"""

    def __init__(self, h: int, w: int, empty: bool = False) -> None:
        """Constructs the set of"""
        self.h = h
        self.w = w
        self.object_mask = np.full((h, w), fill_value=not empty)

    def __sub__(self, other: Set) -> Set:
        if not self.same_size(other):
            raise ValueError("Operation with sets of different sizes.")
        result = Set(self.h, self.w, empty=True)
        result.object_mask = self.object_mask & ~other.object_mask
        return result

    def __isub__(self, other: Set) -> Set:
        if not self.same_size(other):
            raise ValueError("Operation with sets of different sizes.")
        self.object_mask = self.object_mask & ~other.object_mask
        return self

    def __add__(self, other: Set) -> Set:
        if not self.same_size(other):
            raise ValueError("Operation with sets of different sizes.")
        result = Set(self.h, self.w, empty=True)
        result.object_mask = self.object_mask | other.object_mask
        return result

    def __iadd__(self, other: Set) -> Set:
        if not self.same_size(other):
            raise ValueError("Operation with sets of different sizes.")
        self.object_mask |= other.object_mask
        return self

    def get_clipped(self, y: int, x: int, h: int, w: int) -> Set:
        """Returns a clipped set as if it was put in another set of specific size in
        the specific position."""
        yl = abs(min(0, y))
        yr = min(h - y, self.h)
        xl = abs(min(0, x))
        xr = min(w - x, self.w)

        if xl > xr or yl > yr:
            return Set(0, 0)

        clipped = Set(yr - yl, xr - xl, empty=True)
        clipped.object_mask = self.object_mask[yl:yr, xl:xr]
        return clipped

    def same_size(self, other: Set) -> bool:
        """Checks if sets have the same size."""
        return self.h == other.h and self.w == other.w

    def empty(self) -> None:
        """Empties the set."""
        self.object_mask.fill(False)

    def get_frontier_in_direction(self, direction: Direction) -> Set:
        """Returns a subset that borders with background in the direction."""
        moved = self.get_moved(direction.get_opposite())
        frontier = copy(self)
        frontier -= moved
        return frontier

    def get_indexes(self) -> NDArray[np.int32]:
        """Returns indexes of the object in shape (2,<object_size>)."""
        return np.transpose(np.nonzero(self.object_mask))

    def set_indexes(self, indexes: NDArray[np.int32]) -> None:
        """Sets which indexes will represent the set."""
        indexes = np.transpose(indexes)
        self.object_mask[indexes[0], indexes[1]] = True

    def clip_indexes(self, indexes: NDArray[np.int32]) -> NDArray[np.int32]:
        """Returns indexes with those out of bounds removed."""
        return indexes[
            (0 <= indexes[:, 0])
            & (0 <= indexes[:, 1])
            & (indexes[:, 0] < self.h)
            & (indexes[:, 1] < self.w)
        ]

    def get_moved(self, direction: Direction, offset: int = 1) -> Set:
        """Returns a set moved in the direction with the offset."""
        moved = Set(self.h, self.w, True)
        if offset == 0:
            moved.object_mask = self.object_mask
            return moved
        object_indexes = self.get_indexes()
        moved_indexes = object_indexes + direction.coordinates() * offset
        moved_indexes = self.clip_indexes(moved_indexes)
        moved.set_indexes(moved_indexes)
        return moved

    def flip(self) -> None:
        """Flips the set."""
        self.object_mask = np.flip(self.object_mask)

    def get_inner_border(self, connectivity: Connectivity) -> Set:
        """Returns the inner border of the set. A border tile is connected to
        background."""
        kernel = connectivity.get_adjacency_mask()
        border = Set(self.h, self.w, empty=True)
        for i in np.ndindex((self.h, self.w)):
            if not self.object_mask[i]:
                continue
            for k in kernel:
                n = add_tuples(i, k)
                if not self.point_is_in_bbox(*n) or not self.object_mask[n]:
                    border.object_mask[i] = True
        return border

    def subtract(self, y: int, x: int, set: Set) -> None:
        """Subtracts two sets at the given position."""
        self.object_mask[y : y + set.h, x : x + set.w] = (
            self.object_mask[y : y + set.h, x : x + set.w] & ~set.object_mask
        )

    def union(self, y: int, x: int, set: Set) -> None:
        """Performs a union of two sets at the given position."""
        self.object_mask[y : y + set.h, x : x + set.w] = (
            self.object_mask[y : y + set.h, x : x + set.w] & set.object_mask
        )

    def intersection(self, y: int, x: int, set: Set) -> None:
        """Performs an intersection of two sets at the given position."""
        cutout = self.object_mask[y : y + set.h, x : x + set.w].copy()
        self.empty()
        self.object_mask[y : y + set.h, x : x + set.w] = cutout & set.object_mask

    def get_union(self, y: int, x: int, set: Set) -> Set:
        """Returns a union of two sets."""
        union = deepcopy(self)
        union.union(y, x, set)
        return union

    def get_intersection(self, y: int, x: int, set: Set) -> Set:
        """Returns an intersection of two sets."""
        intersection = deepcopy(self)
        intersection.intersection(y, x, set)
        return intersection

    def point_is_in_bbox(self, y: int, x: int) -> bool:
        """Checks whether a point is inside the bounding box of the set."""
        return 0 <= y < self.h and 0 <= x < self.w

    def set_is_in_bbox(self, y: int, x: int, set: Set) -> bool:
        """Checks whether a whole set is inside the bounding box of the
        set."""
        return self.point_is_in_bbox(y, x) and self.point_is_in_bbox(
            y + set.h - 1, x + set.w - 1
        )

    def has_subset(self, y: int, x: int, set: Set) -> bool:
        """Checks whether a given set is a subset of the set."""
        if not self.set_is_in_bbox(y, x, set):
            return False
        return np.all(~set.object_mask | self.object_mask[y : y + set.h, x : x + set.w])

    def collides(self, y: int, x: int, set: Set) -> bool:
        """Checks whether the intersection of two sets is empty."""
        return np.all(
            set.get_clipped(y, x, self.h, self.w).object_mask
            & self.object_mask[max(0, y) : y + set.h, max(0, x) : x + set.w]
        )

    def fit_in(
        self,
        to_fit: Set,
        anchor: Set,
        directions: Tuple = Direction.get_all_directions(),
    ) -> tuple:
        """Fits in another set on the points specified by the anchor in specific
        direction."""
        valid_points = []
        anchor_touch_indexes = anchor.get_indexes()
        for direction in directions:
            set_touch_indexes = to_fit.get_frontier_in_direction(
                direction
            ).get_indexes()
            for i in anchor_touch_indexes:
                for j in set_touch_indexes:
                    origin = subtract_tuples(i, j)
                    if not self.has_subset(origin[0], origin[1], to_fit):
                        continue
                    valid_points.append(origin)
        if valid_points:
            result = random.choice(valid_points)
            return result[0], result[1]
        return None, None

    # TODO Implement another method but without anchor collision check.
    def fit_in_touching(
        self, to_fit: Set, anchor: Set, direction: Direction, offset: int = 0
    ) -> tuple:
        """Fits in another set touching the anchor in the given direction. The new
        set will not collide with the anchor."""
        anchor_touch_set = anchor.get_moved(direction, offset + 1)
        anchor_touch_set -= anchor.get_moved(direction, offset)
        anchor_touch_indexes = anchor_touch_set.get_indexes()

        set_touch_indexes = to_fit.get_frontier_in_direction(
            direction.get_opposite()
        ).get_indexes()

        valid_points = []
        for i in anchor_touch_indexes:
            for j in set_touch_indexes:
                origin = subtract_tuples(i, j)
                if not self.has_subset(origin[0], origin[1], to_fit):
                    continue
                if anchor.collides(origin[0], origin[1], to_fit):
                    continue
                valid_points.append(origin)
        if valid_points:
            result = random.choice(valid_points)
            return result[0], result[1]
        return None, None


def get_random_rectangle_set(dim_range: DimensionRange) -> Set:
    """Generates a random rectangular set of size based of input ranges."""
    width = random.randrange(dim_range.min_w, dim_range.max_w + 1)
    height = random.randrange(dim_range.min_h, dim_range.max_h + 1)
    return Set(height, width)
