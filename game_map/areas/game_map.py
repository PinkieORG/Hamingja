from typing import Tuple

import tile_types
from game_map.areas.area import Area
from game_map.areas.rooms.rooms import Room
from game_map.areas.simple_area import SimpleArea
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

    def make_entrance_between(self, first: Room, second: Room) -> None:
        if first not in self.children or second not in self.children:
            raise ValueError("Rooms not in children.")
        intersection = SimpleArea.intersection(first, second)
        entrance_point = intersection.get_random_coordination()
        entrance = SimpleArea((1, 1), entrance_point)
        entrance.fill(tile_types.yellow)
        self.postfilter.append(entrance)
        # first.make_entrance(entrance_point - first.origin)
        # second.make_entrance(entrance_point - second.origin)

    def make_entrance_room(self, room: Room) -> None:
        for neighbour in self.room_graph.get_neighbours(room):
            self.make_entrance_between(room, neighbour)
