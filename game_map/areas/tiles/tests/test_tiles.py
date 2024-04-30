import unittest

from game_map.areas.tiles.supplementaries import Point
from game_map.areas.tiles.tiles import Tiles
from tile_types import wall, floor, test1


class TestClipped(unittest.TestCase):
    def test_clip_to_same_size(self):
        original = Tiles((10, 5), fill_value=wall)
        clipped = original.clipped(Point(0, 0), (10, 5))
        self.assertEqual(clipped.size, original.size)

    def test_point_inside(self):
        original = Tiles((10, 5), fill_value=wall)
        clipped = original.clipped(Point(5, 2), (10, 5))
        self.assertEqual(clipped.size, (5, 3))

    def test_point_outside_positive(self):
        original = Tiles((10, 5), fill_value=wall)
        clipped = original.clipped(Point(15, 5), (10, 5))
        self.assertEqual(clipped.size, (0, 0))

    def test_point_outside_negative(self):
        original = Tiles((10, 5), fill_value=wall)
        clipped = original.clipped(Point(-5, 0), (10, 5))
        self.assertEqual(clipped.size, (5, 5))

    def test_contains_correct_tiles(self):
        original = Tiles((10, 5), fill_value=wall)
        original.merge(
            Point(0, 0),
            Tiles((1, 1), fill_value=test1),
        )
        clipped = original.clipped(Point(3, 3), (10, 5))
        self.assertEqual(clipped.tiles[0, 0], test1)
