from __future__ import annotations

from typing import Tuple


class Point:
    def __init__(self, y: int, x: int):
        self.y = y
        self.x = x

    def __add__(self, other: Point):
        return Point(self.y + other.y, self.x + other.x)

    @staticmethod
    def from_tuple(tup: Tuple):
        return Point(*tup)


class Size:
    def __init__(self, h: int, w: int):
        if h < 0 or w < 0:
            raise ValueError("Size cannot be negative.")
        self.h = h
        self.w = w

    def __eq__(self, other: Size):
        return self.h == other.h and self.w == other.w

    def tuple(self) -> Tuple:
        return self.h, self.w
