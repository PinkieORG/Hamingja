from __future__ import annotations

from enum import Enum
import random

from utils import FOUR_CONNECTIVITY


class Orientation(Enum):
    VERTICAL = 0
    HORIZONTAL = 1

    def get_axis(self):
        return (self.value + 1) % 2


class Direction(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    def __add__(self, other: Direction) -> Direction:
        result = (self.value + other.value) % 4
        return Direction(result)

    def get_tuple(self):
        return FOUR_CONNECTIVITY[self.value]

    def get_orientation(self) -> Orientation:
        return Orientation(self.value % 2)

    def get_opposite(self) -> Direction:
        result = (self.value + 2) % 4
        return Direction(result)

    def is_neighbour(self, other: Direction) -> bool:
        return ((self.value + 1) % 4 == other.value) or (
            (self.value - 1) % 4 == other.value
        )

    def get_clockwise_neighbour(self):
        return Direction((self.value + 1) % 4)

    def get_counterclockwise_neighbour(self):
        return Direction((self.value - 1) % 4)

    @staticmethod
    def get_random_direction() -> Direction:
        return Direction(random.randrange(0, 4))

    @staticmethod
    def is_horizontal(direction: Direction) -> bool:
        return direction.value % 2 == 1
