from tcod.console import Console

from game_map.areas.area import Area
from game_map.areas.simple_area import SimpleArea


class Renderer:

    def __init__(self, area: SimpleArea):
        self.area = area

    def update(self):
        if isinstance(self.area, Area):
            self.area.draw_children()

    def render_console(self, console: Console):
        self.update()
        tiles = self.area.tiles
        console.rgb[
            tiles.mask
        ] = tiles._tiles["dark"][tiles.mask]
