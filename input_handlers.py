from typing import Optional

import tcod.event

from actions import Action, EscapeAction, MovementAction, MapGenerationAction


class EventHandler(tcod.event.EventDispatch[Action]):
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym

        if key == tcod.event.KeySym.UP:
            action = MovementAction(dy=-1, dx=0)
        elif key == tcod.event.KeySym.DOWN:
            action = MovementAction(dy=1, dx=0)
        elif key == tcod.event.KeySym.LEFT:
            action = MovementAction(dy=0, dx=-1)
        elif key == tcod.event.KeySym.RIGHT:
            action = MovementAction(dy=0, dx=1)

        elif key == tcod.event.KeySym.SPACE:
            action = MapGenerationAction()
        elif key == tcod.event.KeySym.ESCAPE:
            action = EscapeAction()

        return action
