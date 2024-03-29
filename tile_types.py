from typing import Tuple

import numpy as np

graphic_dt = np.dtype(
    [
        ("ch", np.int32),
        ("fg", "3B"),
        ("bg", "3B"),
    ]
)

tile_dt = np.dtype(
    [
        ("walkable", np.bool_),
        ("transparent", np.bool_),
        ("dark", graphic_dt),
    ]
)


def new_tile(
    *,
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types"""
    return np.array((walkable, transparent, dark), dtype=tile_dt)


floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("."), (255, 255, 255), (5, 10, 20)),
)
wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("#"), (255, 255, 255), (5, 10, 20)),
)

void = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord(" "), (255, 255, 255), (0, 128, 0)),
)


object = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("W"), (0, 128, 0), (0, 128, 0)),
)

border = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("B"), (127, 0, 255), (127, 0, 255)),
)
