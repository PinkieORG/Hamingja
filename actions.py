from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class Action:
    def perform(self, engine: Engine, entity: Entity) -> None:
        """Perform this action with the objects needed to determine its scope.

        `engine` is the scope this action is being performed in.

        `entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self, engine: Engine, entity: Entity) -> None:
        raise SystemExit()


class MovementAction(Action):
    def __init__(self, dy: int, dx: int):
        super().__init__()
        self.dy = dy
        self.dx = dx

    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_y = entity.y + self.dy
        dest_x = entity.x + self.dx

        if not engine.game_map.point_is_in_bbox(dest_y, dest_x):
            return
        if not engine.game_map.tiles["walkable"][dest_y, dest_x]:
            return

        entity.move(self.dy, self.dx)
