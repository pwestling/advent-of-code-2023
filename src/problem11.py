import functools
import math
import time
from dataclasses import dataclass
from typing import Optional
from util.search import *

from src.util.search import AdjacentMatrixSearchSpace
from util.resources import resource
from util.timer import timed
from parsec import *
from util.grid import *

input = resource("problem11.txt")
example = """...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#....."""


def solve(s: str, abs=abs) -> int:
    grid = Grid(s.split("\n"))
    empty_rows = set()
    empty_cols = set()
    with timed("Empty find"):
        for i in range(grid.max_x):
          # if every element in row is ".", record row
            if all(grid.get(Point(i,j)) == "." for j in range(grid.max_y)):
                empty_rows.add(i)
        for j in range(grid.max_y):
            if all(grid.get(Point(i,j)) == "." for i in range(grid.max_x)):
                empty_cols.add(j)
        expanded_grid = grid

    with timed("Gal points"):
        galaxy_points = expanded_grid.points_where(lambda x: x == "#")

    with timed("Dist find"):
        sum = 0
        mult = 1000000

        with timed("Expand"):
            for p in galaxy_points:
                for x in empty_rows:
                    if p.x > x:
                        p.x += (mult - 1)
                for y in empty_cols:
                    if p.y > y:
                        p.y += (mult - 1)
        with timed("Add"):
            for i, p1 in enumerate(galaxy_points):
                for j, p2 in enumerate(galaxy_points[i+1:]):
                    cartesian_distance = (p2.x - p1.x) + abs(p1.y - p2.y)
                    sum += cartesian_distance
    return sum


print(solve(example))
with timed():
    print(solve(input))

# wrongs: 9927514 9929476 9926899
# wrongs 2: 16151310 16151228

# correct = 692506533832