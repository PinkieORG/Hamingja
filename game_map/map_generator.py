import logging
import random
from typing import Tuple

from game_map import GameMap
from game_map.areas.random_simple_areas import DimensionRange
from game_map.areas.rooms.rooms import LRoom, Room
from game_map.direction.direction import Direction


class MapGenerator:
    def __init__(
        self, game_map: GameMap, room_size_factors: Tuple[float, float], density: float
    ):
        self.game_map = game_map
        self.room_size_range = DimensionRange.from_size(
            game_map.size, room_size_factors
        )
        self.density = density

    def get_room(self):
        size = self.room_size_range.sample()
        choice = random.random()
        if choice > 0.7:
            room = LRoom(size)
        else:
            room = Room(size)
        return room

    def generate(self):
        logger = logging.getLogger()
        logging.basicConfig(level=logging.INFO)
        start_room = self.get_room()
        self.game_map.place_in_randomly(self.game_map.fit_in(start_room), start_room)
        to_process = set()
        to_process.add(start_room)
        while self.game_map.density() < self.density:
            tries = 0
            neighbour = to_process.pop()
            while tries < 20:
                room = self.get_room()
                placed = self.game_map.place_in_randomly(
                    self.game_map.fit_next_to(room, neighbour), room
                )
                logger.info(
                    ("Tried to place ,", room.size, "at ", room.origin.y, room.origin.x)
                )

                if placed:
                    print("placed ", room.size, "at ", room.origin.y, room.origin.x)
                    to_process.add(room)
                tries += 1
            if len(to_process) == 0:
                return
