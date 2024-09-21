import argparse

from tcod import tcod

from game_map import GameMap
from game_map.map_generators.iterable_generators.room_neighbours_generator import (
    RoomNeighboursGenerator,
)
from renderer import Renderer


def get_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("output_file", help="The text file to save the map to.")
    parser.add_argument("-w", type=int, help="Width of the map.", default=70)
    parser.add_argument("-h", type=int, help="Height of the map.", default=70)
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    game_map = GameMap((args.h, args.w))
    generator = RoomNeighboursGenerator(game_map, (0.1, 0.3), 0.5)
    generator.generate()
    renderer = Renderer(game_map)
    root_console = tcod.console.Console(width=args.h, height=args.w)
    renderer.render_console(root_console)

    with open(args.output_file, "x") as f:
        f.write(root_console.__str__())
