from typing import Any


class Node:
    def __init__(self, value: Any):
        self.value = value
        self.neighbours = []
