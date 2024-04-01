import numpy as np

from game_map.areas.sets.morphology.structural_element import StructuralElement
from game_map.areas.sets.set import Set
from utils import subtract_tuples


def hit_or_miss(set: Set, se: StructuralElement):
    """Hit or Miss morphological operation with the given structural element."""
    if not se.set.point_in_bbox(se.y, se.x):
        raise ValueError(
            "The function does not support the origin outside the "
            "structuring element."
        )
    result = Set(set.h, set.w, empty=True)
    for i in np.ndindex((set.h, set.w)):
        origin = subtract_tuples(i, (se.y, se.x))
        cutout = set.object_mask[
            max(0, origin[0]) : origin[0] + se.set.h,
            max(0, origin[1]) : origin[1] + se.set.w,
        ]
        result.object_mask[i] = np.all(
            cutout == se.set.clipped(origin[0], origin[1], set.h, set.w).object_mask
        )
    return result
