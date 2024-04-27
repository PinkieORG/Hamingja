from typing import Any, List

from utils.graph.node import Node


class Graph:
    def __init__(self):
        self.vertices: List[Node] = []

    def push(self, element: Any, neighbours: List[Any] = None) -> None:
        new_node = Node(element)
        for neighbour in neighbours:
            new_node.add_neighbour(neighbour)
        self.vertices.append(new_node)

    def add_neighbour_to(self, element: Any, neighbour: Any) -> None:
        for vertex in self.vertices:
            if vertex.value == element:
                vertex.add_neighbour(neighbour)
