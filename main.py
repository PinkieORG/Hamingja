#!/usr/bin/env python3
from time import sleep

import tcod


from engine import Engine
from entity import Entity
from game_map import GameMap
from game_map.map_generators.abstract_map_generator import AbstractMapGenerator
from game_map.map_generators.iterable_generators.room_neighbours_generator import (
    RoomNeighboursGenerator,
)
from input_handlers import EventHandler


def main() -> None:
    screen_width = 70
    screen_height = 70

    map_width = 70
    map_height = 70

    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )
    event_handler = EventHandler()

    player = Entity(5, 15, "@", (255, 50, 50))
    npc = Entity(int(2), int(screen_width / 2), "g", (255, 255, 255))
    entities = {npc, player}
    game_map = GameMap((map_height, map_width))

    generator = RoomNeighboursGenerator(game_map, (0.1, 0.3), 0.5)
    generator.generate()

    engine = Engine(
        entities=entities,
        event_handler=event_handler,
        game_map=game_map,
        player=player,
    )

    with tcod.context.new(
        columns=screen_width,
        rows=screen_height,
        tileset=tileset,
        title="Yet Another Roguelike Tutorial",
    ) as context:
        root_console = tcod.console.Console(width=screen_width, height=screen_height)
        while True:
            engine.render(console=root_console, context=context)
            events = tcod.event.wait()
            engine.handle_events(events)


if __name__ == "__main__":
    main()
