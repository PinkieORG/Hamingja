"""Set class."""

from __future__ import annotations

from copy import copy, deepcopy
import random
from typing import Tuple, List

import numpy as np
from numpy.typing import NDArray

from game_map.areas.sets.supplementaries import Size, Point
from game_map.direction.connectivity import Connectivity
from game_map.direction.direction import Direction
from utils import (
    add_tuples,
    subtract_tuples,
)


class Set:
    """Simple binary sets"""

    def __init__(self, size: Size, empty: bool = False) -> None:
        """Constructs the sets of"""
        self.size = size
        self.object_mask = np.full(size.tuple(), fill_value=not empty)

    def __sub__(self, other: Set) -> Set:
        if not self.same_size(other):
            raise ValueError("Operation with sets of different sizes.")
        result = Set(self.size, empty=True)
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
        result = Set(self.size, empty=True)
        result.object_mask = self.object_mask | other.object_mask
        return result

    def __iadd__(self, other: Set) -> Set:
        if not self.same_size(other):
            raise ValueError("Operation with sets of different sizes.")
        self.object_mask |= other.object_mask
        return self

    def __neg__(self):
        result = Set(self.size, empty=True)
        result.object_mask = ~self.object_mask
        return result

    def clipped(self, p: Point, size: Size) -> Set:
        """Returns a clipped sets as if it was put in another sets of specific size in
        the specific position."""
        yl = abs(min(0, p.y))
        yr = min(size.h - p.y, self.size.h)
        xl = abs(min(0, p.x))
        xr = min(size.w - p.x, self.size.w)

        if xl > xr or yl > yr:
            return Set(Size(0, 0))

        clipped = Set(Size(yr - yl, xr - xl), empty=True)
        clipped.object_mask = self.object_mask[yl:yr, xl:xr]
        return clipped

    def same_size(self, other: Set) -> bool:
        """Checks if sets have the same size."""
        return self.size == other.size

    def empty(self) -> None:
        """Empties the sets."""
        self.object_mask.fill(False)

    def frontier_in_direction(self, direction: Direction) -> Set:
        """Returns a subset that borders with background in the direction."""
        moved = self.moved(direction.get_opposite())
        frontier = copy(self)
        frontier -= moved
        return frontier

    def get_indexes(self) -> NDArray[np.int32]:
        """Returns indexes of the object in shape (2,<object_size>)."""
        return np.transpose(np.nonzero(self.object_mask))

    def set_indexes(self, indexes: NDArray[np.int32]) -> None:
        """Sets which indexes will represent the sets."""
        indexes = np.transpose(indexes)
        self.object_mask[indexes[0], indexes[1]] = True

    def clip_indexes(self, indexes: NDArray[np.int32]) -> NDArray[np.int32]:
        """Returns indexes with those out of bounds removed."""
        return indexes[
            (0 <= indexes[:, 0])
            & (0 <= indexes[:, 1])
            & (indexes[:, 0] < self.size.h)
            & (indexes[:, 1] < self.size.w)
        ]

    def moved(self, direction: Direction, offset: int = 1) -> Set:
        """Returns a sets moved in the direction with the offset."""
        moved = Set(self.size, True)
        if offset == 0:
            moved.object_mask = self.object_mask
            return moved
        object_indexes = self.get_indexes()
        moved_indexes = object_indexes + direction.coordinates() * offset
        moved_indexes = self.clip_indexes(moved_indexes)
        moved.set_indexes(moved_indexes)
        return moved

    def flip(self) -> None:
        """Flips the sets."""
        self.object_mask = np.flip(self.object_mask)

    def inner_border(self, connectivity: Connectivity = Connectivity.EIGHT) -> Set:
        """Returns the inner border of the sets. A border tile is the one connected to
        background."""
        kernel = connectivity.get_adjacency_mask()
        border = Set(self.size, empty=True)
        for i in np.ndindex(self.size.tuple()):
            if not self.object_mask[i]:
                continue
            for k in kernel:
                n = add_tuples(i, k)
                if not self.point_in_bbox(Point(n[0], n[1])) or not self.object_mask[n]:
                    border.object_mask[i] = True
                    break
        return border

    def corners(self, direction: Direction) -> Set:
        """Returns corners of the set in a given direction. The direction and its
        clockwise neighbour specifies the corner orientation."""
        from game_map.areas.sets.morphology.structural_element import corner_se
        from game_map.areas.sets.morphology.operations import hit_or_miss

        return hit_or_miss(self, corner_se(direction))

    def subtract(self, p: Point, set: Set) -> None:
        """Subtracts two sets at the given position."""
        self.object_mask[p.y : p.y + set.size.h, p.x : p.x + set.size.w] = (
            self.object_mask[p.y : p.y + set.size.h, p.x : p.x + set.size.w]
            & ~set.object_mask
        )

    def unify(self, p: Point, set: Set) -> None:
        """Performs a union of two sets at the given position."""
        self.object_mask[p.y : p.y + set.size.h, p.x : p.x + set.size.w] = (
            self.object_mask[p.y : p.y + set.size.h, p.x : p.x + set.size.w]
            | set.object_mask
        )

    def intersect(self, p: Point, set: Set) -> None:
        """Performs an intersection of two sets at the given position."""
        cutout = self.object_mask[p.y : p.y + set.size.h, p.x : p.x + set.size.w].copy()
        self.empty()
        self.object_mask[p.y : p.y + set.size.h, p.x : p.x + set.size.w] = (
            cutout & set.object_mask
        )

    def difference(self, p: Point, set: Set) -> Set:
        difference = deepcopy(self)
        difference.subtract(p, set)
        return difference

    def union(self, p: Point, set: Set) -> Set:
        """Returns a union of two sets."""
        union = deepcopy(self)
        union.unify(p, set)
        return union

    def intersection(self, p: Point, set: Set) -> Set:
        """Returns an intersection of two sets."""
        intersection = deepcopy(self)
        intersection.intersect(p, set)
        return intersection

    def point_in_bbox(
        self,
        p: Point,
    ) -> bool:
        """Checks whether a point is inside the bounding box of the sets."""
        return 0 <= p.y < self.size.h and 0 <= p.x < self.size.w

    def set_in_bbox(self, p: Point, set: Set) -> bool:
        """Checks whether a whole sets is inside the bounding box of the
        sets."""
        return self.point_in_bbox(p) and self.point_in_bbox(
            Point(p.y + set.size.h - 1, p.x + set.size.w - 1)
        )

    def has_subset(self, p: Point, set: Set) -> bool:
        """Checks whether a given sets is a subset of the sets."""
        if not self.set_in_bbox(p, set):
            return False
        return np.all(
            ~set.object_mask
            | self.object_mask[p.y : p.y + set.size.h, p.x : p.x + set.size.w]
        )

    def collides(self, p: Point, set: Set) -> bool:
        """Checks whether the intersection of two sets is empty."""
        return np.all(
            set.clipped(p, self.size).object_mask
            & self.object_mask[
                max(0, p.y) : p.y + set.size.h, max(0, p.x) : p.x + set.size.w
            ]
        )

    def transform(self, p: Point, size: Size) -> None:
        transformed = Set(size, True)
        transformed.unify(p, self)
        self.size = size
        self.object_mask = transformed.object_mask

    def fit_in(
        self,
        to_fit: Set,
        anchor: Set,
        directions: Tuple = Direction.get_all_directions(),
    ) -> List[Point]:
        """Fits in another sets on the points specified by the anchor in specific
        direction."""
        valid_points = []
        anchor_touch_indexes = anchor.get_indexes()
        for direction in directions:
            set_touch_indexes = to_fit.frontier_in_direction(
                direction.get_opposite()
            ).get_indexes()
            for i in anchor_touch_indexes:
                for j in set_touch_indexes:
                    origin = Point(*subtract_tuples(i, j))
                    if not self.has_subset(origin, to_fit):
                        continue
                    valid_points.append(origin)
        return valid_points

    def fit_in_touching(
        self, to_fit: Set, anchor: Set, direction: Direction, offset: int = 0
    ) -> Point | None:
        """Fits in another sets touching the anchor in the given direction. The new
        sets will not collide with the anchor."""
        anchor_touch_set = anchor.moved(direction, offset + 1)
        anchor_touch_set -= anchor.moved(direction, offset)
        anchor_touch_indexes = anchor_touch_set.get_indexes()

        set_touch_indexes = to_fit.frontier_in_direction(
            direction.get_opposite()
        ).get_indexes()

        valid_points = []
        for i in anchor_touch_indexes:
            for j in set_touch_indexes:
                origin = Point(*subtract_tuples(i, j))
                if not self.has_subset(origin, to_fit):
                    continue
                if anchor.collides(origin, to_fit):
                    continue
                valid_points.append(origin)
        if valid_points:
            result = random.choice(valid_points)
            return result
        return None

    def fit_in_touching_border(
        self,
        to_fit: Set,
        direction: Direction,
        border_offset: int = 0,
    ) -> Point | None:
        """Fits in another areas touching the inner border with"""
        return self.fit_in_touching(
            to_fit, self.inner_border(), direction, border_offset
        )

    def fit_in_corner(
        self, to_fit: Set, directions: Tuple = Direction.get_all_directions()
    ) -> Point | None:
        """Places an areas in the corner. The areas will be touching the wall
        in defined direction and the next wall clockwise of that direction.
        For example: if direction is NORTH then the areas will be touching
        NORTH and EAST walls."""

        result = []
        for direction in directions:
            result += self.fit_in(
                to_fit, self.corners(direction), (direction.get_opposite(),)
            )
        if result:
            result = random.choice(result)
            return result
        return None
