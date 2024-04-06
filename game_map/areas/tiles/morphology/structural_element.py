import numpy as np
from numpy.typing import NDArray

from game_map.areas.tiles.supplementaries import Point
from game_map.areas.tiles.tiles import Tiles
from game_map.direction.direction import Direction


class StructuralElement:
    def __init__(self, mask: NDArray[np.int32], origin: Point):
        self.tiles = Tiles((mask.shape[0], mask.shape[1]))
        self.tiles.tiles["mask"] = mask
        self.origin = origin

    @property
    def size(self):
        return self.tiles.size

    @property
    def h(self):
        return self.tiles.h

    @property
    def w(self):
        return self.tiles.w


def corner_se(direction: Direction):
    return CORNER_MASKS[direction.value]


CORNER_MASKS = [
    StructuralElement(np.array([[0, 0], [1, 0]]), Point(1, 0)),
    StructuralElement(np.array([[1, 0], [0, 0]]), Point(0, 0)),
    StructuralElement(np.array([[0, 1], [0, 0]]), Point(0, 1)),
    StructuralElement(np.array([[0, 0], [0, 1]]), Point(1, 1)),
]
