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

input = resource("problem18.txt")
example = """R 6 (#70c710)
D 5 (#0dc571)
L 2 (#5713f0)
D 2 (#d2c081)
R 2 (#59c680)
D 2 (#411b91)
L 5 (#8ceee2)
U 2 (#caa173)
L 1 (#1b58a2)
U 2 (#caa171)
R 2 (#7807d2)
U 3 (#a77fa3)
L 2 (#015232)
U 2 (#7a21e3)"""

@dataclass
class Instruction:
    direction: Point
    distance: int
    color: str

def parse(s: str) -> list[Instruction]:
    lines = s.strip().split("\n")
    result = []
    for line in lines:
        parts = line.split(" ")
        direction = line[0]
        dir = None
        if direction == "R":
            dir = RIGHT
        elif direction == "L":
            dir = LEFT
        elif direction == "U":
            dir = UP
        elif direction == "D":
            dir = DOWN

        distance = int(parts[1])
        color = parts[2]
        result.append(Instruction(dir, distance, color))
    return result

def visualize(grid: numpy.ndarray) -> str:
    # find the max and min x and y values where elements are set
    max_x, max_y, min_x, min_y = get_max_min(grid)

    subgrid = grid[min_x-1:max_x+2, min_y-1:max_y+2]
    result = ""
    for i in range(subgrid.shape[0]):
        for j in range(subgrid.shape[1]):
            result += "#" if subgrid[i, j][0] == "(" else subgrid[i, j]
        result += "\n"
    print(result)


def get_max_min(grid):
    min_x = None
    max_x = None
    min_y = None
    max_y = None
    for i in range(grid.shape[0]):
        if (grid[i, :] != " ").any():
            min_x = i
            break
    for i in range(grid.shape[0] - 1, -1, -1):
        if (grid[i, :] != " ").any():
            max_x = i
            break
    for i in range(grid.shape[1]):
        if (grid[:, i] != " ").any():
            min_y = i
            break
    for i in range(grid.shape[1] - 1, -1, -1):
        if (grid[:, i] != " ").any():
            max_y = i
            break
    print(min_x, max_x, min_y, max_y)
    return max_x, max_y, min_x, min_y


def in_polygon(grid: numpy.ndarray, p: Point, min_x: int) -> bool:
    if grid[p.x, p.y] != " ":
        return True
    crossings = 0
    in_boundary = False
    for i in range(p.x, max(min_x-4, 0), -1):
        if not in_boundary and grid[i, p.y] != " ":
            in_boundary = True
        elif in_boundary and grid[i, p.y] == " ":
            in_boundary = False
            crossings += 1
    return crossings % 2 == 1


def flood_fill(grid: numpy.ndarray, start: Point) -> numpy.ndarray:
    max_x, max_y, min_x, min_y = get_max_min(grid)
    max_x += 5
    max_y += 5
    min_x -= 5
    min_y -= 5
    visited = numpy.full((max_x + 1, max_y + 1), False, dtype=bool)
    queue = [start]
    while queue:
        p = queue.pop(0)
        if p.x >= min_x and p.y >= min_y and p.x <= max_x and p.y <= max_y and not visited[p.x, p.y] and grid[p.x, p.y] == " ":
            visited[p.x, p.y] = True
            for d in [UP, DOWN, LEFT, RIGHT]:
                queue.append(p + d)
    return visited


def solve1(s: str) -> int:
    instructions = parse(s)
    size = 20000
    grid = numpy.full((size, size), " ", dtype=str, )
    location = Point(size//2, size//2)
    for instruction in instructions:
        print(instruction)
        for i in range(instruction.distance):
            grid[location.x, location.y] = instruction.color
            location += instruction.direction
    visualize(grid)

    max_x, max_y, min_x, min_y = get_max_min(grid)
    # sum = 0
    # for i in range(min_x-1, max_x + 1):
    #     for j in range(min_y-1, max_y + 1):
    #         if in_polygon(grid, Point(i, j), min_x):
    #             sum += 1
    print("area", (max_x - min_x + 1) * (max_y - min_y + 1))


    flood = flood_fill(grid, Point(min_x-1,min_y-1))
    print(flood)

    c = grid.copy()
    c[min_x, min_y] = "*"
    count = 0
    for i in range(min_x, max_x + 1):
        for j in range(min_y, max_y + 1):
            if not flood[i, j]:
                count += 1
                c[i, j] = "#"
    visualize(c)


    return count

# print(solve1(example))
print(solve1(input))

# 70336 is wrong