from typing import Tuple

import tile_types
from game_map.areas.area import Area
from game_map.areas.rooms.rooms import Room
from utils.graph.graph import Graph


class GameMap(Area):
    def __init__(self, size: Tuple):
        super().__init__(size)
        self.fill(tile_types.wall)
        self.room_graph = Graph()

    def place_room(self, room: Room) -> None:
        super().place_in(room)
        self.room_graph.push(room)

    def place_room_next_to(self, to_place: Room, neighbour: Room) -> bool:
        placed = self.place_in_randomly(self.fit_next_to(to_place, neighbour), to_place)
        if placed:
            self.room_graph.push(to_place, [neighbour])
            self.room_graph.add_neighbour_to(neighbour, to_place)
        return placed
