from __future__ import annotations

import numpy as np

import tile_types
from game_map.areas.sets.set import Set, Direction


def from_set(set, fill_value):
    area = Area(set.h, set.w)
    area.object_mask = set.object_mask
    area.fill(fill_value=fill_value)
    return area


class Area(Set):
    """Represent an areas of tiles."""

    def __init__(self, h: int, w: int, empty: bool = False):
        super().__init__(h, w, empty)
        self.parent = None
        self.children = []
        self.tiles = np.full((h, w), fill_value=tile_types.void)

    def fill_border(self, fill_value) -> None:
        """Sets border of the sets to have specific value."""
        border = from_set(self.inner_border(), fill_value)
        self.place_in(0, 0, border)

    def fill_in(self, y: int, x: int, set: Set, fill_value) -> None:
        """Fills the sets with s value in areas defined by the given sets."""
        self.tiles[y : y + set.h, x : x + set.w] = np.where(
            set.object_mask,
            fill_value,
            self.tiles[y : y + set.h, x : x + set.w],
        )

    def fill(self, fill_value) -> None:
        """Fills the sets with a value in sets areas"""
        self.tiles = np.where(
            self.object_mask,
            np.full((self.h, self.w), fill_value=fill_value),
            self.tiles,
        )

    def fill_background(self, fill_value) -> None:
        """Fills the sets with a value through the whole bounding box."""
        self.tiles = np.full((self.h, self.w), fill_value=fill_value)

    def place_in_background(self, y: int, x: int, area: Area) -> None:
        """Places another areas inside the bounding box without sets check."""
        if not self.point_in_bbox(y, x) or not self.point_in_bbox(
            y + area.h - 1, x + area.w - 1
        ):
            raise ValueError("Area to insert does not fit inside the bounding box.")
        self.children.append(area)
        self.tiles[y : y + area.h, x : x + area.w] = area.tiles

    def place_in(self, y: int, x: int, area: Area) -> None:
        """Places another areas inside the sets."""
        if not self.has_subset(y, x, area):
            raise ValueError("Area to insert does not fit inside the sets.")
        self.tiles[y : y + area.h, x : x + area.w] = np.where(
            area.object_mask,
            area.tiles,
            self.tiles[y : y + area.h, x : x + area.w],
        )

    def fit_in_touching_border(
        self,
        to_fit: Area,
        direction: Direction,
        border_offset: int = 0,
    ):
        """Fits in another areas touching the inner border with"""
        return self.fit_in_touching(
            to_fit, self.inner_border(), direction, border_offset
        )
