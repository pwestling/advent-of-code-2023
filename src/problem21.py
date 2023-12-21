import functools
import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from util.search import *

from src.util.search import AdjacentMatrixSearchSpace
from util.resources import resource
from util.timer import timed
# from parsec import *
from util.grid import *
import itertools
from tqdm import tqdm
from scipy.sparse import dok_matrix

input = resource("problem21.txt")

example = """...........
.....###.#.
.###.##..#.
..#.#...#..
....#.#....
.##..S####.
.##..#...#.
.......##..
.##.#.####.
.##..##.##.
..........."""

import sys
sys.setrecursionlimit(100000)

def num_reachable(cache: dict, grid: numpy.ndarray, point: Point, steps: int) -> set[Point]:
    if (point, steps) in cache:
        return cache[(point, steps)]
    if steps == 0:
        return {point}
    else:
        dirs = [UP, DOWN, LEFT, RIGHT]
        adjacent = [point+d for d in dirs if is_inside(grid, point+d) and grid[(point+d).x, (point+d).y] != "#"]
        result = set()
        for p in adjacent:
            result.update(num_reachable(cache, grid, p, steps - 1))
        cache[(point, steps)] = result
        return result


def solve(s: str, num_steps: int) -> int:
    grid = numpy.array([[c for c in line] for line in s.splitlines()])
    start = None
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            if grid[x, y] == "S":
                start = Point(x, y)
                break
    reachable = num_reachable({}, grid, start, num_steps)
    return len(reachable)

print(solve(example, 64))
print(solve(input, 64))