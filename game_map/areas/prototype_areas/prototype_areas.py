from typing import Tuple

import tile_types
from game_map.areas.simple_area import SimpleArea


def create_carpet(size: Tuple) -> SimpleArea:
    carpet = SimpleArea(size)
    carpet.fill(tile_types.carpet)
    return carpet


def create_column() -> SimpleArea:
    column = SimpleArea((2, 2))
    column.fill(tile_types.wall)
    return column
