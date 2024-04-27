from typing import Any, List

from utils.graph.node import Node


class Graph:
    def __init__(self):
        self.vertices: List[Node] = []

    def push(self, element: Any):
        self.vertices.append(Node(element))
