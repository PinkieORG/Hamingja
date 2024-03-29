import random

import numpy as np

from area import Area
from dimensions import DimensionRange


class Rectangle(Area):
    def __init__(self, h: int, w: int, tile_type):
        super().__init__(h, w)
        self.tiles = np.full((h, w), fill_value=tile_type)


class RandomRectangle(Rectangle):
    def __init__(self, dim_range: DimensionRange, tile_type):
        width = random.randrange(dim_range.min_w, dim_range.max_w + 1)
        height = random.randrange(dim_range.min_h, dim_range.max_h + 1)
        super().__init__(width, height, tile_type)
