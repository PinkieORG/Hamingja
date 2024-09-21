import logging
from abc import abstractmethod
from typing import Tuple

from game_map import GameMap
from game_map.map_generators.abstract_map_generator import AbstractMapGenerator


class IterableGenerator(AbstractMapGenerator):
    def __init__(
        self,
        game_map: GameMap,
        room_size_factors: Tuple[float, float],
        density: float,
    ):
        super().__init__(game_map, room_size_factors, density)
        self.logger = logging.getLogger()
        logging.basicConfig(level=logging.INFO)

    @abstractmethod
    def prepare(self):
        pass

    @abstractmethod
    def add_room(self):
        pass

    def generate(self):
        self.prepare()
        while self.game_map.density() < self.density:
            self.add_room()
