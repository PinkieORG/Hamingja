from __future__ import annotations

import random
from copy import copy

import numpy as np

from dimensions import DimensionRange
from direction import Direction
from utils import (
    add_tuples,
    get_adjacency_mask,
    subtract_tuples,
)


class Set:
    def __init__(self, h: int, w: int, empty: bool = False):
        self.h = h
        self.w = w
        self.object_mask = np.full((h, w), fill_value=not empty)

    def empty(self):
        self.object_mask.fill(False)

    def get_inner_border_directional(self, direction: Direction):
        moved = self.get_moved(direction.get_opposite())
        border = copy(self)
        border.minus(moved)
        return border

    def get_object_indexes(self):
        return np.transpose(np.nonzero(self.object_mask))

    def set_object_indexes(self, indexes: list):
        indexes = np.transpose(indexes)
        self.object_mask[indexes[0], indexes[1]] = True

    def minus(self, set):
        self.object_mask = np.where(set.object_mask, False, self.object_mask)

    def clip_indexes(self, indexes):
        return indexes[
            (0 <= indexes[:, 0])
            & (0 <= indexes[:, 1])
            & (indexes[:, 0] < self.w)
            & (indexes[:, 1] < self.h)
        ]

    def get_moved(self, direction: Direction, offset: int = 1) -> Set:
        moved = Set(self.h, self.w, True)
        object_indexes = self.get_object_indexes()
        moved_indexes = object_indexes + direction.get_tuple() * offset
        moved_indexes = self.clip_indexes(moved_indexes)
        moved.set_object_indexes(moved_indexes)
        return moved

    def flip(self):
        self.object_mask = np.flip(self.object_mask)

    def get_inner_border(self, connectivity):
        kernel = get_adjacency_mask(connectivity)
        border = Set(self.h, self.w, empty=True)
        for i in np.ndindex((self.h, self.w)):
            if not self.object_mask[i]:
                continue
            for k in kernel:
                n = add_tuples(i, k)
                if not self.point_is_in_bbox(*n) or not self.object_mask[n]:
                    border.object_mask[i] = True
        return border

    def minus_subset(self, y, x, set):
        self.object_mask[y : y + set.h, x : x + set.w] = np.where(
            set.object_mask,
            False,
            self.object_mask[y : y + set.h, x : x + set.w],
        )

    def plus_subset(self, y, x, set):
        self.object_mask[y : y + set.h, x : x + set.w] = np.where(
            set.object_mask,
            True,
            self.object_mask[y : y + set.h, x : x + set.w],
        )

    def point_is_in_bbox(self, y: int, x: int):
        return 0 <= y < self.h and 0 <= x < self.w

    def set_is_in_bbox(self, y: int, x: int, set):
        return self.point_is_in_bbox(y, x) and self.point_is_in_bbox(
            y + set.h - 1, x + set.w - 1
        )

    def is_inside(self, y, x, set):
        if not self.set_is_in_bbox(y, x, set):
            return False
        mask = (
            ~set.object_mask | self.object_mask[y : y + set.h, x : x + set.w]
        )
        return np.all(mask)

    # TODO collision outside bbox.
    def collides(self, y, x, set):
        if not self.set_is_in_bbox(y, x, set):  # doesn't make sense
            return True
        mask = set.object_mask & self.object_mask[y : y + set.h, x : x + set.w]
        return np.any(mask)

    def fit_in_touching(
        self,
        to_fit: Set,
        anchor: Set,
        direction: Direction,
        offset: int = 1,
    ):

        touch_points = anchor.get_moved(direction, 1)
        touch_points.minus(anchor)
        # touch_points = touch_points.get_moved(
        #    direction.get_orientation(), offset
        # )

        touch_indexes = touch_points.get_object_indexes()

        to_fit_border = to_fit.get_inner_border_directional(
            direction.get_opposite()
        ).get_object_indexes()

        valid_points = []

        for i in touch_indexes:
            for j in to_fit_border:
                origin = subtract_tuples(i, j)
                if not self.is_inside(origin[0], origin[1], to_fit):
                    continue
                if anchor.collides(origin[0], origin[1], to_fit):
                    continue
                valid_points.append(origin)

        if valid_points:
            result = random.choice(valid_points)
            return result[0], result[1]
        return None, None


class RandomRectangleSet(Set):
    def __init__(self, dim_range: DimensionRange):
        width = random.randrange(dim_range.min_w, dim_range.max_w + 1)
        height = random.randrange(dim_range.min_h, dim_range.max_h + 1)
        super().__init__(height, width)
