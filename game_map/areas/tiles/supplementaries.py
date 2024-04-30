from __future__ import annotations

from typing import Tuple


class Point:
    def __init__(self, y: int, x: int):
        self.y = y
        self.x = x

    def __add__(self, other: Point):
        return Point(self.y + other.y, self.x + other.x)

    def __sub__(self, other: Point):
        return Point(self.y - other.y, self.x - other.x)

    @staticmethod
    def from_tuple(tup: Tuple):
        return Point(*tup)
