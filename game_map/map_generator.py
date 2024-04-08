import random
from typing import Tuple

from game_map.areas.area import Area
from game_map.areas.random_simple_areas import DimensionRange
from game_map.areas.rooms.rooms import LRoom, Room


class MapGenerator:
    def __init__(
        self, area: Area, room_size_factors: Tuple[float, float], density: float
    ):
        self.area = area
        self.room_size_range = DimensionRange.from_size(area.size, room_size_factors)
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
        start_room = self.get_room()
        self.area.place_in_randomly(self.area.fit_in(start_room), start_room)
        neighbour = start_room
        tries = 0
        while self.area.density() < self.density:
            room = self.get_room()
            placed = False
            while not placed:
                placed = self.area.place_in_randomly(
                    self.area.fit_next_to(room, neighbour), room
                )
                if tries > 7:
                    return
                else:
                    tries += 1
            neighbour = room
