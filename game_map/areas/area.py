from __future__ import annotations

import random
from typing import List

import numpy as np
from tcod.console import Console

import tile_types
from game_map.areas.sets.set import Set
from game_map.areas.sets.supplementaries import Size, Point
from game_map.direction.direction import Direction


def from_set(set, fill_value):
    area = Area(set.size)
    area.object_mask = set.object_mask
    area.fill(fill_value=fill_value)
    return area


class Area(Set):
    """Represent an areas of tiles."""

    def __init__(self, size: Size, empty: bool = False, origin: Point = Point(0, 0)):
        super().__init__(size, empty)
        self.origin = origin
        self.parent = None
        self.children = []
        self.tiles = np.full(size.tuple(), fill_value=tile_types.void)

    def fill_border(self, fill_value) -> None:
        """Sets border of the sets to have specific value."""
        border = from_set(self.inner_border(), fill_value)
        self.place_in(Point(0, 0), border)

    def fill_in(self, p: Point, set: Set, fill_value) -> None:
        """Fills the sets with s value in areas defined by the given sets."""
        self.tiles[p.y : p.y + set.size.h, p.x : p.x + set.size.w] = np.where(
            set.object_mask,
            fill_value,
            self.tiles[p.y : p.y + set.size.h, p.x : p.x + set.size.w],
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

    def place_in_background(self, p: Point, area: Area) -> None:
        """Places another areas inside the bounding box without sets check."""
        if not self.point_in_bbox(p) or not self.point_in_bbox(
            Point(p.y + area.size.h - 1, p.x + area.size.w - 1)
        ):
            raise ValueError("Area to insert does not fit inside the bounding box.")
        self.tiles[p.y : p.y + area.size.h, p.x : p.x + area.size.w] = area.tiles

    def place_in(self, p: Point, area: Area) -> None:
        """Places another areas inside the sets."""
        if not self.has_subset(p, area):
            raise ValueError("Area to insert does not fit inside the sets.")
        area.origin = p
        self.children.append(area)

    def render(self, console: Console, parent_origin: Point):
        global_origin = parent_origin + self.origin
        console.rgb[
            global_origin.y : global_origin.y + self.size.h,
            global_origin.x : global_origin.x + self.size.w,
        ] = np.where(
            self.object_mask,
            self.tiles["dark"],
            console.rgb[
                global_origin.y : global_origin.y + self.size.h,
                global_origin.x : global_origin.x + self.size.w,
            ],
        )
        for child in self.children:
            child.render(console, self.origin)

    def place_next_to(
        self,
        to_place: Area,
        neighbour: Area,
        direction: Direction = Direction.get_random_direction(),
    ):
        if neighbour not in self.children:
            raise ValueError("Neighbour not in children.")

        frontier = neighbour.frontier_in_direction(direction)
        frontier.transform(neighbour.origin, self.size)

        clone = self.difference(neighbour.origin, neighbour)
        clone += frontier

        points = clone.fit_in(to_place, frontier, (direction,))

        self.place_in_randomly(points, to_place)

    def place_in_randomly(self, place_points: List[Point], area: Area) -> bool:
        if len(place_points) != 0:
            p = random.choice(place_points)
            self.place_in(p, area)
            return True
        return False
