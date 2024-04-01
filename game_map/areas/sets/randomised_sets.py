import random

from game_map.areas.sets.set import Set


class DimensionRange:
    def __init__(self, min_h, max_h, min_w, max_w):

        self.min_h = min_h
        self.max_h = max_h
        self.min_w = min_w
        self.max_w = max_w


def random_rectangle_set(dim_range: DimensionRange) -> Set:
    """Generates a random rectangular sets of size based of input ranges."""
    width = random.randrange(dim_range.min_w, dim_range.max_w + 1)
    height = random.randrange(dim_range.min_h, dim_range.max_h + 1)
    return Set(height, width)
