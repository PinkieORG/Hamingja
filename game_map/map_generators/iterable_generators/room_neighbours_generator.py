import logging
import random
from typing import Tuple

from game_map import GameMap
from game_map.areas.rooms.rooms import LRoom, Room
from game_map.map_generators.iterable_generators.iterable_generator import (
    IterableGenerator,
)
from tile_types import active_room, wall, red


class RoomNeighboursGenerator(IterableGenerator):
    def __init__(
        self, game_map: GameMap, room_size_factors: Tuple[float, float], density: float
    ):
        super().__init__(game_map, room_size_factors, density)
        self.to_process: list[Room] = []

    def get_room(self):
        size = self.room_size_range.sample()
        choice = random.random()
        if choice > 0.7:
            room = LRoom(size)
        else:
            room = Room(size)
        return room

    def prepare(self):
        start_room = self.get_room()
        self.game_map.place_in_randomly(self.game_map.fit_in(start_room), start_room)
        self.to_process.append(start_room)

    def add_room(self):
        if len(self.to_process) == 0:
            self.logger.info("No more rooms to process.")
            return
        tries = 0
        if __debug__:
            for room in self.to_process:
                room.fill_border(active_room)
        neighbour = random.choice(self.to_process)
        if __debug__:
            neighbour.fill_border(active_room)
        while tries < 20:
            room = self.get_room()
            placed = self.game_map.place_room_next_to(room, neighbour)
            self.logger.info(
                ("Tried to place ,", room.size, "at ", room.origin.y, room.origin.x)
            )
            if placed:
                self.logger.info(
                    ("placed ", room.size, "at ", room.origin.y, room.origin.x)
                )
                self.to_process.append(room)
                return
            tries += 1
        self.to_process.remove(neighbour)
        if __debug__:
            neighbour.fill_border(wall)
