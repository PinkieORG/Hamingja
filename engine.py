from typing import Set, Iterable, Any

from tcod.console import Console
from tcod.context import Context

from entity import Entity
from game_map import GameMap

from input_handlers import EventHandler
from renderer import Renderer


class Engine:
    def __init__(
        self,
        entities: Set[Entity],
        event_handler: EventHandler,
        game_map: GameMap,
        player: Entity,
    ):
        self.entities = entities
        self.event_handler = event_handler
        self.game_map = game_map
        self.player = player
        self.renderer = Renderer(game_map)

    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue
            action.perform(self, self.player)

    def render(self, console: Console, context: Context) -> None:
        self.renderer.render_console(console)

        for entity in self.entities:
            console.print(y=entity.y, x=entity.x, string=entity.char, fg=entity.color)

        context.present(console)

        console.clear()
