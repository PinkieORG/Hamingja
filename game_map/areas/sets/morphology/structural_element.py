import numpy as np
from numpy.typing import NDArray

from game_map.areas.sets.set import Set
from game_map.areas.sets.supplementaries import Size, Point
from game_map.direction.direction import Direction


class StructuralElement:
    def __init__(self, mask: NDArray[np.int32], origin: Point):
        self.set = Set(Size(mask.shape[0], mask.shape[1]))
        self.set.object_mask = mask
        self.origin = origin


def corner_se(direction: Direction):
    return CORNER_MASKS[direction.value]


CORNER_MASKS = [
    StructuralElement(np.array([[0, 0], [1, 0]]), Point(0, 1)),
    StructuralElement(np.array([[1, 0], [0, 0]]), Point(0, 0)),
    StructuralElement(np.array([[0, 1], [0, 0]]), Point(1, 0)),
    StructuralElement(np.array([[0, 0], [0, 1]]), Point(1, 1)),
]
