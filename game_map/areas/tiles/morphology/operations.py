import numpy as np

from game_map.areas.tiles.morphology.structural_element import StructuralElement
from game_map.areas.tiles.supplementaries import Point
from utils.utils import subtract_tuples


def hit_or_miss(in_tiles, se: StructuralElement):
    """Hit or Miss morphological operation with the given structural element."""
    if not se.tiles.point_in_bbox(se.origin):
        raise ValueError(
            "The function does not support the origin outside the "
            "structuring element."
        )
    result = np.full(in_tiles.shape, fill_value=False)
    for i in np.ndindex(in_tiles.shape):
        o = subtract_tuples(i, (se.origin.y, se.origin.x))
        cutout = in_tiles[
            max(0, o[0]) : o[0] + se.h,
            max(0, o[1]) : o[1] + se.w,
        ]
        result[i] = np.all(
            cutout
            == se.tiles.clipped(Point(o[0], o[1]), in_tiles.shape)[0].mask
        )
    return result
