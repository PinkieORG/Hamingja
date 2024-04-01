import operator
import sys
from enum import Enum

import numpy as np


def get_indexes_of_set(set):
    return np.where(set.object_mask)


def to_tuples(array):
    return list(map(tuple, array))


def add_tuples(a, b):
    return tuple(map(operator.add, a, b))


def subtract_tuples(a, b):
    return tuple(map(operator.sub, a, b))


def in_bounds(shape, pos):
    return 0 <= pos[0] < shape[0] and 0 <= pos[1] < shape[1]


def distance_swipe(dist_map, kernel):
    for i in np.ndindex(dist_map.shape):
        min_n = sys.maxsize
        for k in kernel:
            n_i = add_tuples(i, k)
            if in_bounds(dist_map.shape, n_i) and dist_map[n_i] < min_n:
                min_n = dist_map[n_i]
        dist_map[i] = min(min_n + 1, dist_map[i])


def get_distance_map(array, connectivity):
    if connectivity == "4":
        kernel = [(-1, 0), (0, -1)]
    elif connectivity == "8":
        kernel = [(-1, 0), (-1, -1), (0, -1), (2, -1)]
    else:
        raise ValueError("Invalid connectivity.")
    dist_map = np.where(array, sys.maxsize, 0)
    distance_swipe(dist_map, kernel)
    distance_swipe(np.flip(dist_map), kernel)
    return dist_map


def transform_coordinates(y, x, origin_x, origin_y):
    return y - origin_x, x - origin_y
