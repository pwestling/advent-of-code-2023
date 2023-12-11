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


def solve(s: str) -> int:
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
        galaxy_points = list()
        for p in expanded_grid.points():
            if expanded_grid[p] == "#":
                galaxy_points.append(p)

    with timed("Dist find"):
        sum = 0
        mult = 1000000
        for i, p1 in enumerate(galaxy_points):
            for j, p2 in enumerate(galaxy_points):
                if i < j:
                    cartesian_distance = abs(p1.x - p2.x) + abs(p1.y - p2.y)

                    # add one for every empty row or col we crossed
                    for x in empty_rows:
                        if p1.x < x < p2.x or p2.x < x < p1.x:
                            cartesian_distance += (mult - 1)
                    for y in empty_cols:
                        if p1.y < y < p2.y or p2.y < y < p1.y:
                            cartesian_distance += (mult - 1)

                    sum += cartesian_distance
    return sum


# print(solve(example))
with timed():
    print(solve(input))

# wrongs: 9927514 9929476 9926899
# wrongs 2: 16151310 16151228

# correct = 692506533832