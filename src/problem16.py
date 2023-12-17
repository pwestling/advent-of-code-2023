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
import itertools
from tqdm import tqdm

input = resource("problem16.txt")
example = """.|...\....
|.-.\.....
.....|-...
........|.
..........
.........\\
..../.\\\\..
.-.-/..|..
.|....-|.\\
..//.|...."""

@dataclass
class PathNode:
    point: Point
    parent: "PathNode"
    children: list["PathNode"]

def is_inside(grid: np.ndarray, p: Point) -> bool:
    return 0 <= p.x < grid.shape[0] and 0 <= p.y < grid.shape[1]

def trace_beam(grid: np.ndarray, current: Point, direction: Point, energized_tiles: set[tuple[Point, Point]], path_parent: PathNode) -> None:
    if not is_inside(grid, current):
        return
    here = grid[current.x, current.y]
    if (current, direction) in energized_tiles:
        return
    energized_tiles.add((current, direction))

    if here == ".":
        next = current + direction
        node = PathNode(current, path_parent, [])
        path_parent.children.append(node)
        trace_beam(grid, next, direction, energized_tiles, node)
    elif here == "/":
        if direction == UP:
            next = current + RIGHT
            direction = RIGHT
        elif direction == DOWN:
            next = current + LEFT
            direction = LEFT
        elif direction == LEFT:
            next = current + DOWN
            direction = DOWN
        elif direction == RIGHT:
            next = current + UP
            direction = UP
        node = PathNode(current, path_parent, [])
        path_parent.children.append(node)
        trace_beam(grid, next, direction, energized_tiles, node)
    elif here == "\\":
        if direction == UP:
            next = current + LEFT
            direction = LEFT
        elif direction == DOWN:
            next = current + RIGHT
            direction = RIGHT
        elif direction == LEFT:
            next = current + UP
            direction = UP
        elif direction == RIGHT:
            next = current + DOWN
            direction = DOWN
        node = PathNode(current, path_parent, [])
        path_parent.children.append(node)
        trace_beam(grid, next, direction, energized_tiles, node)
    elif here == "|":
        if direction == UP or direction == DOWN:
            next = current + direction
            node = PathNode(current, path_parent, [])
            path_parent.children.append(node)
            trace_beam(grid, next, direction, energized_tiles, node)
        else:
            for d in [UP, DOWN]:
                next = current + d
                node = PathNode(current, path_parent, [])
                path_parent.children.append(node)
                trace_beam(grid, next, d, energized_tiles, node)
    elif here == "-":
        if direction == LEFT or direction == RIGHT:
            next = current + direction
            node = PathNode(current, path_parent, [])
            path_parent.children.append(node)
            trace_beam(grid, next, direction, energized_tiles, node)
        else:
            for d in [LEFT, RIGHT]:
                next = current + d
                node = PathNode(current, path_parent, [])
                path_parent.children.append(node)
                trace_beam(grid, next, d, energized_tiles, node)

def solve_one(s: str) -> int:
    return solve(to_numpy(s), Point(0, 0), RIGHT)
def solve(grid: np.ndarray, start: Point, dir: Point) -> int:
    energized_tiles: set[tuple[Point, Point]] = set()
    path_root = PathNode(Point(0, 0), None, [])
    trace_beam(grid, start, dir, energized_tiles, path_root)
    return len({p for p, _ in energized_tiles})

import sys
sys.setrecursionlimit(6000)

print(solve_one(example))
print(solve_one(input))


def solve2(s: str) -> int:
    grid = to_numpy(s)
    results : list[tuple[Point, int]] = []
    # try every edge point
    for i in range(grid.shape[0]):
        j = 0
        results.append((Point(i, j), solve(grid, Point(i, j), RIGHT)))
        j = grid.shape[1] - 1
        results.append((Point(i, j), solve(grid, Point(i, j), LEFT)))
    for j in range(grid.shape[1]):
        i = 0
        results.append((Point(i, j), solve(grid, Point(i, j), DOWN)))
        i = grid.shape[0] - 1
        results.append((Point(i, j), solve(grid, Point(i, j), UP)))
    return max([score for _, score in results])

print(solve2(example))
print(solve2(input))

