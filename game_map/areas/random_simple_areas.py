from __future__ import annotations

import random
from typing import Tuple

from game_map.areas.area import SimpleArea


class DimensionRange:
    def __init__(self, min_h, max_h, min_w, max_w):
        self.min_h = min_h
        self.max_h = max_h
        self.min_w = min_w
        self.max_w = max_w

    @staticmethod
    def from_size(size: Tuple, factors: Tuple[float, float]) -> DimensionRange:
        return DimensionRange(
            int(size[0] * factors[0]),
            int(size[0] * factors[1]),
            int(size[1] * factors[0]),
            int(size[1] * factors[1]),
        )

    def sample(self) -> Tuple:
        h = random.randrange(self.min_h, self.max_h)
        w = random.randrange(self.min_w, self.max_w)
        return h, w


def random_rectangle_area(dim_range: DimensionRange) -> SimpleArea:
    """Generates a random rectangular tiles of size based of input ranges."""
    return SimpleArea(dim_range.sample())
