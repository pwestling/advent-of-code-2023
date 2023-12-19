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
from scipy.sparse import dok_matrix

class SparseGrid:

    points: dict[Point, int]
    by_y_value: dict[int, list[Point]]
    by_x_value: dict[int, list[Point]]

    def __init__(self):
        self.points = {}
        self.by_y_value = {}
        self.by_x_value = {}

    def __getitem__(self, p: Point) -> int:
        return self.points.get(p, 0)

    def __setitem__(self, p: Point, value: int):
        self.points[p] = value
        xvals = self.by_x_value.get(p.x, [])
        xvals.append(p)
        self.by_x_value[p.x] = xvals
        yvals = self.by_y_value.get(p.y, [])
        yvals.append(p)
        self.by_y_value[p.y] = yvals

    def set_row_range(self, x: int, start: int, end: int, value: int):
        for i in range(start, end+1):
            self[Point(x, i)] = value

    def set_col_range(self, y: int, start: int, end: int, value: int):
        for i in range(start, end+1):
            self[Point(i, y)] = value

    def get_row(self, x: int) -> list[Point]:
        return self.by_x_value.get(x, [])

    def get_col(self, y: int) -> list[Point]:
        return self.by_y_value.get(y, [])

    def min_x(self) -> int:
        return min(self.by_x_value.keys())

    def max_x(self) -> int:
        return max(self.by_x_value.keys())

    def min_y(self) -> int:
        return min(self.by_y_value.keys())

    def max_y(self) -> int:
        return max(self.by_y_value.keys())

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

    def to_part_2(self):
        hex_code = self.color[2:]
        dist = hex_code[:5]
        dir = hex_code[5]

        new_dist = x = int(dist, 16)
        new_dir = None
        if dir == "0":
            new_dir = RIGHT
        elif dir == "1":
            new_dir = DOWN
        elif dir == "2":
            new_dir = LEFT
        elif dir == "3":
            new_dir = UP
        return Instruction(new_dir, new_dist, self.color)



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

def visualize(grid: SparseGrid) -> str:
    # find the max and min x and y values where elements are set
    max_x, max_y, min_x, min_y = get_max_min(grid)

    result = ""
    for i in range(min_x-1, max_x+2):
        for j in range(min_y-1, max_y+2):
            val = grid[Point(i, j)]
            if val == 1:
                result += "#"
            elif val == 0:
                result += " "
            else:
                result += "@"
        result += "\n"
    print(result)


def get_max_min(grid: SparseGrid):
    # min_x = None
    # max_x = None
    # min_y = None
    # max_y = None
    # for i in range(grid.shape[0]):
    #     if (grid[i, :].toarray() != 0).any():
    #         min_x = i
    #         break
    # for i in range(grid.shape[0] - 1, -1, -1):
    #     if (grid[i, :].toarray() != 0).any():
    #         max_x = i
    #         break
    # for i in range(grid.shape[1]):
    #     if (grid[:, i].toarray() != 0).any():
    #         min_y = i
    #         break
    # for i in range(grid.shape[1] - 1, -1, -1):
    #     if (grid[:, i].toarray() != 0).any():
    #         max_y = i
    #         break
    return grid.max_x(), grid.max_y(), grid.min_x(), grid.min_y()



def flood_fill(grid: SparseGrid, start: Point) -> SparseGrid:
    max_x, max_y, min_x, min_y = get_max_min(grid)
    max_x += 5
    max_y += 5
    min_x -= 5
    min_y -= 5
    visited = SparseGrid()
    queue = [start]
    while queue:
        p = queue.pop(0)
        if p.x < min_x or p.y < min_y or p.x > max_x or p.y > max_y:
           return None
        if not visited[p] and (grid[p] == 0 or grid[p] is None):
            visited[p] = True
            for d in [UP, DOWN, LEFT, RIGHT]:
                queue.append(p + d)
    return visited


def solve1(s: str) -> int:
    instructions = parse(s)
    size = 20000
    return solve_shoelace(instructions)


# 70336 is wrong

def solve2(s: str) -> int:
    instructions = [i.to_part_2() for i in  parse(s)]
    size = 200_000_000
    return solve_shoelace(instructions)
def solve(size: int, instructions: list[Instruction]) -> int:
    grid = SparseGrid()
    # grid = numpy.zeros((size, size), dtype=int)
    location = Point(0,0)
    for instruction in instructions:
        print(instruction)
        next_point = location + mult_point(instruction.direction, instruction.distance)
        # set every point on the line between location and next_point to "#"

        start_x = min(location.x, next_point.x)
        end_x = max(location.x, next_point.x)
        start_y = min(location.y, next_point.y)
        end_y = max(location.y, next_point.y)
        if start_x == end_x:
            grid.set_row_range(start_x, start_y, end_y, 1)
        elif start_y == end_y:
            grid.set_col_range(start_y, start_x, end_x, 1)
        location = next_point

    max_x, max_y, min_x, min_y = get_max_min(grid)
    area = (max_x - min_x + 1) * (max_y - min_y + 1)
    print("area",area)
    print(min_x, max_x, min_y, max_y)

    if area < 100000:
        visualize(grid)


    flood = None
    iter = grid.points.keys().__iter__()
    while flood is None:
        point = next(iter)
        possibilites = [point+UP, point+DOWN, point+LEFT, point+RIGHT]
        possibilites = [p for p in possibilites if grid[p] == 0]
        for p in possibilites:
            print("Trying flood fill from", p, "...")
            flood = flood_fill(grid, p)
            if flood is not None:
                break

    # flood = flood_fill(grid, Point((max_x-min_x)//2,(max_y-min_y)//2))

    c = SparseGrid()
    count = 0
    for i in range(min_x, max_x + 1):
        for j in range(min_y, max_y + 1):
            if flood[Point(i, j)]:
                count += 1
                c[Point(i, j)] = 1
    if area < 100000:
        visualize(c)

    return count + len(grid.points.keys())

def solve_shoelace(instructions: list[Instruction]) -> int:

    location = Point(0,0)
    list_of_points = []
    for instruction in instructions:
        # print(instruction)
        dist = instruction.distance
        # if instruction.direction == RIGHT or instruction.direction == LEFT:
        #     dist += 1
        next_point = location + mult_point(instruction.direction, dist)
        list_of_points.append(next_point)
        location = next_point
        # for i in range(dist):
        #     location += instruction.direction
        #     list_of_points.append(location)
    # g = SparseGrid()
    # for p in list_of_points:
    #     g[p] = 1
    # visualize(g)

    # list_of_points.reverse()
    print("shoes")
    result = 0
    dists = 0
    for i in range(len(list_of_points)):
        p1 = list_of_points[i]
        p2 = list_of_points[i+1] if i+1 < len(list_of_points) else list_of_points[0]
        det = (p1.x * p2.y) - (p2.x * p1.y)
        result += det
        d = abs(p1.x - p2.x) + abs(p1.y - p2.y)
        # if i < len(list_of_points) // 2 + 1:
        #     print(d)
        #     dists += abs(p1.x - p2.x) + abs(p1.y - p2.y)
        dists += d
        # dists += abs(p1.x - p2.x) + abs(p1.y - p2.y)
    # dists += abs(list_of_points[-1].x - list_of_points[0].x) + abs(list_of_points[-1].y - list_of_points[0].y)
    print(len(instructions), dists)
    return (abs(result) // 2) + dists // 2 + 1

e = solve1(example)
if e != 62:
    print("example failed", e)
    # exit(1)
else:
    print(e)
print(solve1(input))

print(solve2(example))
print(solve2(input))

# 952408259439 too low
