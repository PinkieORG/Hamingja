from __future__ import annotations

import random
from copy import deepcopy, copy
from typing import List, Union, Tuple

from tcod.console import Console

from game_map.areas.tiles.simple_area import SimpleArea
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

    # TODO: What happens to the children?
    # def __sub__(self, other: Area) -> Area:
    #     if not self.is_related(other):
    #         raise ValueError("Invalid operation.")
    #     if self.parent is other.parent and self.parent is not None:
    #         result_set = Set.__sub__(
    #             self.transformed(self.origin, self.parent.size),
    #             other.transformed(other.origin, self.parent.size),
    #         )
    #         copy = deepcopy(self).transformed(self.origin,self.parent.size)
    #
    #         result = Area.create_from_set(result_set)
    #
    #         for child in self.children:
    #
    #         result_set.tighten()
    #         if result_set.size.is_zero():
    #             return Area(Size(0, 0), True)
    #         return result
    #
    #     if self is other.parent:
    #        result_set = super().__sub__(other.transformed(other.origin, other.parent))
    #         result = deepcopy(self)
    #         result.object_mask = deepcopy(result_set.object_mask)
    #         return result
    #     if other is self.parent:
    #         return other - self

    # TODO method to merge tiles from children.

    # def place_in_background(self, p: Point, area: Area) -> None:
    #     """Places another areas inside the bounding box without tiles check."""
    #     if not self.point_in_bbox(p) or not self.point_in_bbox(
    #         Point(p.y + area.size.h - 1, p.x + area.size.w - 1)
    #     ):
    #         raise ValueError("Area to insert does not fit inside the bounding box.")
    #     self.tiles[p.y : p.y + area.size.h, p.x : p.x + area.size.w] = area.tiles

    def place_in(self, area: Area) -> None:
        """Places another areas inside the tiles."""
        if not self.fits_in(area):
            raise ValueError("Area to insert does not fit inside the tiles.")
        area.parent = self
        self.children.append(area)

    def remove(self, area: Area) -> Union[Area, None]:
        if area in self.children:
            self.children.remove(area)
        return None

    def render(self, console: Console, parent_origin: Point):
        global_origin = parent_origin + self.origin
        self.tiles.render(console, global_origin)
        for child in self.children:
            child.render(console, self.origin)

    def place_in_randomly(self, place_points: List[Point], area: Area) -> bool:
        if len(place_points) != 0:
            p = random.choice(place_points)
            area.origin = p
            self.place_in(area)
            return True
        return False

    def fits_in(self, area: Area) -> bool:
        """Checks whether a given tiles is a subset of the tiles."""
        return self.tiles.is_subset(area.origin, area.tiles)

    def collides(self, area: Area) -> bool:
        """Checks whether the intersection of two tiles is empty."""
        return self.tiles.collides(area.origin, area.tiles)

    def fit_in_direction(
        self,
        to_fit: SimpleArea,
        anchor: SimpleArea,
        directions: Tuple = Direction.get_all_directions(),
    ) -> List[Point]:
        """Fits in another tiles on the points specified by the anchor in specific
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
        """Fits in another tiles touching the anchor in the given direction. The new
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
        """Fits in another areas touching the inner border with"""
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

    def fit_next_to(
        self,
        to_place: SimpleArea,
        neighbour: SimpleArea,
        direction: Direction = Direction.get_random_direction(),
    ) -> List[Point]:
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
