from typing import Tuple


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    def __init__(self, y: int, x: int, char: str, color: Tuple[int, int, int]):
        self.y = y
        self.x = x
        self.char = char
        self.color = color

    def move(self, dy: int, dx: int) -> None:
        self.y += dy
        self.x += dx
