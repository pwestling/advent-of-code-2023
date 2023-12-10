import functools
import math
import time
from dataclasses import dataclass
from typing import Optional
from search.search import *

from util.resources import resource
from util.timer import timed
from parsec import *

input = resource("problem10.txt")
example = """.....
.S-7.
.|.|.
.L-J.
....."""

@dataclass
class Point:
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))

# | is a vertical pipe connecting north and south.
# - is a horizontal pipe connecting east and west.
# L is a 90-degree bend connecting north and east.
# J is a 90-degree bend connecting north and west.
# 7 is a 90-degree bend connecting south and west.
# F is a 90-degree bend connecting south and east.
# . is ground; there is no pipe in this tile.
# S is the starting position of the animal; there is a pipe on this tile, but your sketch doesn't show what shape the pipe has.

def to_graph(s: str) -> tuple[dict[Point, list[Point]], Point]:
    lines = s.split("\n")
    start = None
    result = {}
    for i in range(len(lines)):
        for j in range(len(lines[i])):
            result[Point(i, j)] = []
            if lines[i][j] == "S":
                start = Point(i, j)
            if lines[i][j] == "|":
                if i > 0:
                    result[Point(i, j)].append(Point(i-1, j))
                if i < len(lines)-1:
                    result[Point(i, j)].append(Point(i+1, j))
            if lines[i][j] == "-":
                if j > 0:
                    result[Point(i, j)].append(Point(i, j-1))
                if j < len(lines[i])-1:
                    result[Point(i, j)].append(Point(i, j+1))
            if lines[i][j] == "L":
                if i > 0:
                    result[Point(i, j)].append(Point(i-1, j))
                if j < len(lines[i])-1:
                    result[Point(i, j)].append(Point(i, j+1))
            if lines[i][j] == "J":
                if i > 0:
                    result[Point(i, j)].append(Point(i-1, j))
                if j > 0:
                    result[Point(i, j)].append(Point(i, j-1))
            if lines[i][j] == "7":
                if i < len(lines)-1:
                    result[Point(i, j)].append(Point(i+1, j))
                if j > 0:
                    result[Point(i, j)].append(Point(i, j-1))
            if lines[i][j] == "F":
                if i < len(lines)-1:
                    result[Point(i, j)].append(Point(i+1, j))
                if j < len(lines[i])-1:
                    result[Point(i, j)].append(Point(i, j+1))
    for k, adjlist in result.items():
        for p in adjlist:
            if p == start:
                result[start].append(k)
    return result, start

def solve(s: str) -> int:
    g, start = to_graph(s)
    space = AdjenctMatrixSearchSpace(g, start, None)
    result = all_distance_bfs_search(space, start)
    return max(result.values())


print(solve(example))
print(solve(input))

def add_point(p: Point, d: Point) -> Point:
    return Point(p.x + d.x, p.y + d.y)

def assign_glyph(s: str, p: Point, n: str) -> str:
    lines = s.split("\n")
    return "\n".join(lines[:p.x] + [lines[p.x][:p.y] + n + lines[p.x][p.y+1:]] + lines[p.x+1:])

def dir_cross_counter(graph: dict[Point, list[Point]], loop: set[Point], max_x:int, max_y:int) -> tuple[Callable[[Point, Point, Point], bool], list[int]]:
    call_count = [0]
    @functools.cache
    def dir_cross_count_recur(p: Point, d: Point, side: Point) -> int:
        call_count[0] += 1
        current = add_point(p, d)
        if 0 <= current.x < max_x and 0 <= current.y < max_y:
            if current in loop:
                adj_list = graph[current]
                if add_point(current, side) in adj_list:
                    return 1 + dir_cross_count_recur(current, d, side)
            return dir_cross_count_recur(current, d, side)
        else:
            return 0
    def dir_cross_answer(p: Point, d: Point, side: Point) -> bool:
        return dir_cross_count_recur(p, d, side) % 2 == 1
    return dir_cross_answer, call_count

def solve2(s: str) -> int:
    g, start = to_graph(s)
    space = AdjenctMatrixSearchSpace(g, start, None)
    result = all_distance_bfs_search(space, start)
    # the loop consists of all points which are reachable from start, i.e. all keys of this map
    loop = set(result.keys())
    lines = s.split("\n")
    max_x = len(lines)
    max_y = len(lines[0])
    points_in_loop = set()
    dir_cross_count_is_odd, call_count = dir_cross_counter(g, loop, max_x, max_y)
    left = Point(0, -1)
    right = Point(0, 1)
    up = Point(-1, 0)
    down = Point(1, 0)
    for i in range(max_x):
        for j in range(max_y):
            # Walk outwards along each cardinal direction until we either hit the edge or part of the loop

            point = Point(i, j)

            if dir_cross_count_is_odd(point, up, left, ) and \
                dir_cross_count_is_odd(point, up, right, ) and \
                dir_cross_count_is_odd(point, down, left, ) and \
                dir_cross_count_is_odd(point, down, right, ) and \
                dir_cross_count_is_odd(point, right, up, ) and \
                dir_cross_count_is_odd(point, right, down, ) and \
                dir_cross_count_is_odd(point, left, up, ) and \
                dir_cross_count_is_odd(point, left, down, ):

                points_in_loop.add(point)


    # visualize(loop, max_x, max_y, points_in_loop, s)
    return len(points_in_loop)


def visualize(loop, max_x, max_y, points_in_loop, s):
    viz = s
    for x in range(max_x):
        for y in range(max_y):
            p = Point(x, y)
            if p in loop:
                viz = assign_glyph(viz, p, "L")
            elif Point(x, y) in points_in_loop:
                viz = assign_glyph(viz, p, "I")
            else:
                viz = assign_glyph(viz, p, "0")
    print(viz)


example2 = """...........
.S-------7.
.|F-----7|.
.||.....||.
.||.....||.
.|L-7.F-J|.
.|..|.|..|.
.L--J.L--J.
..........."""

example3 = """.F----7F7F7F7F-7....
.|F--7||||||||FJ....
.||.FJ||||||||L7....
FJL7L7LJLJ||LJ.L-7..
L--J.L7...LJS7F-7L7.
....F-J..F7FJ|L7L7L7
....L7.F7||L7|.L7L7|
.....|FJLJ|FJ|F7|.LJ
....FJL-7.||.||||...
....L---J.LJ.LJLJ..."""

example4 = """FF7FSF7F7F7F7F7F---7
L|LJ||||||||||||F--J
FL-7LJLJ||||||LJL-77
F--JF--7||LJLJIF7FJ-
L---JF-JLJIIIIFJLJJ7
|F|F-JF---7IIIL7L|7|
|FFJF7L7F-JF7IIL---7
7-L-JL7||F7|L7F-7F7|
L.L7LFJ|||||FJL7||LJ
L7JLJL-JLJLJL--JLJ.L"""

# print(solve2(example2))
# print(solve2(example3))

print(solve2(example4))

with timed():
    print(solve2(input))







