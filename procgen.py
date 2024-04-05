import random

import numpy as np

import tile_types
from game_map import GameMap


def create_room():
    width = random.randrange(78, 79)
    height = random.randrange(43, 44)

    return np.full((width, height), fill_value=tile_types.floor)


def place_room(game_map: GameMap, room):
    y = random.randrange(1, game_map.h - room.shape[0])
    x = random.randrange(1, game_map.w - room.shape[1])

    game_map.tiles[y : y + room.shape[0], x : x + room.shape[1]] = room
