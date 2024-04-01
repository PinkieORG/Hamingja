from __future__ import annotations

import random
from typing import List

import numpy as np

import tile_types
from game_map.areas.sets.set import Set
from game_map.areas.sets.supplementaries import Size


def from_set(set, fill_value):
    area = Area(set.size)
    area.object_mask = set.object_mask
    area.fill(fill_value=fill_value)
    return area


class Area(Set):
    """Represent an areas of tiles."""

    def __init__(self, size: Size, empty: bool = False):
        super().__init__(size, empty)
        self.parent = None
        self.children = []
        self.tiles = np.full(size.tuple(), fill_value=tile_types.void)

    def fill_border(self, fill_value) -> None:
        """Sets border of the sets to have specific value."""
        border = from_set(self.inner_border(), fill_value)
        self.place_in(0, 0, border)

    def fill_in(self, y: int, x: int, set: Set, fill_value) -> None:
        """Fills the sets with s value in areas defined by the given sets."""
        self.tiles[y : y + set.size.h, x : x + set.size.w] = np.where(
            set.object_mask,
            fill_value,
            self.tiles[y : y + set.size.h, x : x + set.size.w],
        )

    def fill(self, fill_value) -> None:
        """Fills the sets with a value in sets areas"""
        self.tiles = np.where(
            self.object_mask,
            np.full(self.size.tuple(), fill_value=fill_value),
            self.tiles,
        )

    def fill_background(self, fill_value) -> None:
        """Fills the sets with a value through the whole bounding box."""
        self.tiles = np.full(self.size.tuple(), fill_value=fill_value)

    def place_in_background(self, y: int, x: int, area: Area) -> None:
        """Places another areas inside the bounding box without sets check."""
        if not self.point_in_bbox(y, x) or not self.point_in_bbox(
            y + area.size.h - 1, x + area.size.w - 1
        ):
            raise ValueError("Area to insert does not fit inside the bounding box.")
        self.children.append(area)
        self.tiles[y : y + area.size.h, x : x + area.size.w] = area.tiles

    def place_in(self, y: int, x: int, area: Area) -> None:
        """Places another areas inside the sets."""
        if not self.has_subset(y, x, area):
            raise ValueError("Area to insert does not fit inside the sets.")
        self.tiles[y : y + area.size.h, x : x + area.size.w] = np.where(
            area.object_mask,
            area.tiles,
            self.tiles[y : y + area.size.h, x : x + area.size.w],
        )

    # def place_next_to(
    #     self,
    #     to_place: Set,
    #     neighbour: Set,
    #     direction: Direction = Direction.get_random_direction(),
    # ):
    #     neighbour.frontier_in_direction(direction)
    #     # clone = self.difference()

    def place_in_randomly(self, place_points: List, area: Area) -> bool:
        if len(place_points) != 0:
            point = random.choice(place_points)
            self.place_in(point[0], point[1], area)
            return True
        return False
