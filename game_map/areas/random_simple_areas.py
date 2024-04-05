import random

from game_map.areas.area import SimpleArea
from game_map.areas.tiles.tiles import Tiles


class DimensionRange:
    def __init__(self, min_h, max_h, min_w, max_w):
        self.min_h = min_h
        self.max_h = max_h
        self.min_w = min_w
        self.max_w = max_w


def random_rectangle_area(dim_range: DimensionRange) -> SimpleArea:
    """Generates a random rectangular tiles of size based of input ranges."""
    h = random.randrange(dim_range.min_h, dim_range.max_h)
    w = random.randrange(dim_range.min_w, dim_range.max_w)
    return SimpleArea((h, w))
