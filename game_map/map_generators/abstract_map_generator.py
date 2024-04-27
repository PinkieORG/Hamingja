from abc import ABC, abstractmethod
from typing import Tuple

from game_map import GameMap
from game_map.areas.random_simple_areas import DimensionRange


class AbstractMapGenerator(ABC):
    def __init__(
        self, game_map: GameMap, room_size_factors: Tuple[float, float], density: float
    ):
        self.game_map = game_map
        self.room_size_range = DimensionRange.from_size(
            game_map.size, room_size_factors
        )
        self.density = density

    @abstractmethod
    def get_room(self):
        pass

    @abstractmethod
    def generate(self):
        pass
