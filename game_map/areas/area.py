from __future__ import annotations

import random
from copy import deepcopy, copy
from typing import List, Union, Tuple

from tcod.console import Console

from game_map.areas.simple_area import SimpleArea
from game_map.areas.tiles.supplementaries import Point
from game_map.direction.direction import Direction


class Area(SimpleArea):
    """Represent an areas on the game map. It can have its subareas inside and a
    parent, creating a tree structure. It has its origin which defines a position
    within the parent."""

    def __init__(self, size: Tuple, origin: Point = Point(0, 0)):
        super().__init__(size, origin)
        self.children = []

    def is_related(self, other: Area) -> bool:
        return (
            self.parent is not other.parent
            or other is not self.parent
            or other not in self.children
        )

    # def place_in_background(self, p: Point, area: Area) -> None:
    #     """Places another areas inside the bounding box without tiles check."""
    #     if not self.point_in_bbox(p) or not self.point_in_bbox(
    #         Point(p.y + area.size.h - 1, p.x + area.size.w - 1)
    #     ):
    #         raise ValueError("Area to insert does not fit inside the bounding box.")
    #     self.tiles[p.y : p.y + area.size.h, p.x : p.x + area.size.w] = area.tiles

    def place_in(self, area: SimpleArea) -> None:
        """Places another areas inside the tiles."""
        if not self.is_placable(area):
            raise ValueError("Area to insert does not fit inside the tiles.")
        area.parent = self
        self.children.append(area)
        self.set_unplaceable(area.uncover())

    def remove(self, area: Area) -> Union[Area, None]:
        if area in self.children:
            self.children.remove(area)
        return None

    def render(self, console: Console, parent_origin: Point) -> None:
        global_origin = parent_origin + self.origin
        self.tiles.render(console, global_origin)
        for child in self.children:
            child.render(console, self.origin)

    def place_in_randomly(self, place_points: List[Point], area: SimpleArea) -> bool:
        if len(place_points) != 0:
            p = random.choice(place_points)
            area.origin = p
            self.place_in(area)
            return True
        return False

    def is_placable(self, area: SimpleArea) -> bool:
        """Checks whether a given tiles is a subset of the tiles."""
        return self.tiles.is_placable(area.origin, area.tiles)

    def fits_in(self, area: SimpleArea) -> bool:
        """Checks whether a given tiles is a subset of the tiles."""
        return self.tiles.is_subset(area.origin, area.tiles)

    def collides(self, area: Area) -> bool:
        """Checks whether the intersection of two tiles is empty."""
        return self.tiles.collides(area.origin, area.tiles)

    def fit_next_to(
        self,
        to_place: SimpleArea,
        neighbour: SimpleArea,
        direction: Direction = None,
    ) -> List[Point]:
        """Fits in another area next to a given child of this area."""
        if direction is None:
            direction = Direction.get_random_direction()
        if neighbour not in self.children:
            raise ValueError("Neighbour not in children.")

        frontier = SimpleArea.create_from_tiles(
            neighbour.tiles.frontier_in_direction(direction)
        )
        frontier.origin = copy(neighbour.origin)
        frontier.parent = self
        clone = deepcopy(self)
        clone.fill_out(neighbour)
        clone.fill_in(frontier)
        return clone.fit_in_direction(to_place, frontier, (direction,))
