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

blank = """...........
...........
...........
...........
...........
.....S.....
...........
...........
...........
...........
..........."""



import sys
sys.setrecursionlimit(100000)

def wrap(point: Point, shape: tuple[int, int]) -> Point:
    return Point(point.x % shape[0], point.y % shape[1])

def num_reachable(cache: dict, grid: numpy.ndarray, point: Point, steps: int) -> set[Point]:
    wrapped_point = Point(point.x % grid.shape[0], point.y % grid.shape[1])
    if (wrapped_point, steps) in cache:
        prev_point, prev_result = cache[(wrapped_point, steps)]
        vector = point - prev_point
        adjusted_result = {p + vector for p in prev_result}
        return adjusted_result
    if steps == 0:
        return {point}
    else:
        dirs = [UP, DOWN, LEFT, RIGHT]
        adjacent_points = [point+d for d in dirs]
        wrapped_points = [Point(p.x, p.y ) for p in adjacent_points]
        adjacent = [p for p in wrapped_points if grid[p.x % grid.shape[0], p.y % grid.shape[1]] != "#"]
        result = set()
        for p in adjacent:
            result.update(num_reachable(cache, grid, p, steps - 1))
        cache[(wrapped_point, steps)] = (point, result)
        return result

def tesseltate(grid: numpy.ndarray, side_length: int) -> numpy.ndarray:
    result = numpy.zeros((grid.shape[0] * side_length, grid.shape[1] * side_length), dtype=object)
    for x in range(result.shape[0]):
        for y in range(result.shape[1]):
            result[x , y] = grid[x % grid.shape[0], y % grid.shape[1]]
    return result

def visualize(grid: numpy.ndarray, reachable: set[Point], num_steps) -> None:
    visualize_helper(grid, reachable, 3, num_steps)

def find_start(grid):
    start = None
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            if grid[x, y] == "S":
                start = Point(x, y)
                break
    return start

grid = numpy.array([[c for c in line] for line in input.splitlines()])
start = find_start(grid)
pointcounts = []
wrapped_point_counts = []
almost_reachable_counts = []
wrapped_point_sets = []
almost_reachable_sets = []
harder_reachable_counts = []
for i in range(0, grid.shape[0] * 3):
    # find every rock that is cartesian distance i from start
    points = set()
    almost_reachable = set()
    harder_reach = set()
    check_points = []

    for k in range(0, i):
        p1 = Point(start.x + k, start.y - i + k)

        p2 = Point(start.x - k, start.y - i + k)

        p3 = Point(start.x - i + k, start.y + k)
        p4 = Point(start.x + i - k, start.y + k)
        for p in [p1, p2, p3, p4]:
            wraped = wrap(p, grid.shape)
            if grid[wraped.x, wraped.y] == "#":
                points.add(p)
            else:
                # move the point one column closer to the start
                col_adjust = 1 if p.y < start.y else (-1 if p.y > start.y else 0)
                row_adjust = 1 if p.x < start.x else (-1 if p.x > start.x else 0)
                p_adj_col = wrap(Point(p.x, p.y + col_adjust), grid.shape)
                p_adj_row = wrap(Point(p.x + row_adjust, p.y), grid.shape)
                if grid[p_adj_col.x, p_adj_col.y] == "#" and grid[p_adj_row.x, p_adj_row.y] == "#":
                    almost_reachable.add(wrap(p, grid.shape))

                padj_col2 = wrap(Point(p.x, p.y + col_adjust * 2), grid.shape)
                padj_row2 = wrap(Point(p.x + row_adjust * 2, p.y), grid.shape)
                oadj_diag = wrap(Point(p.x + row_adjust, p.y + col_adjust), grid.shape)
                if grid[padj_col2.x, padj_col2.y] == "#" and grid[padj_row2.x, padj_row2.y] == "#" and grid[oadj_diag.x, oadj_diag.y] == "#":
                    harder_reach.add(wrap(p, grid.shape))



    wrapped_points = set(wrap(p, grid.shape) for p in points)
    wrapped_point_sets.append(wrapped_points)
    pointcounts.append(len(points))
    wrapped_point_counts.append(len(wrapped_points))
    almost_reachable_counts.append(len(almost_reachable))
    almost_reachable_sets.append(almost_reachable)
    harder_reachable_counts.append(len(harder_reach))

def visualize_helper(grid: numpy.ndarray, reachable: set[Point], side_len: int, step) -> None:
    mult = side_len // 2
    visual = tesseltate(grid, side_len)
    max_x = -math.inf
    max_y = -math.inf
    min_x = math.inf
    min_y = math.inf
    for p in reachable:
            dist = abs(p.x - start.x) + abs(p.y - start.y)
            # if dist != step:
            #     continue
        # try:
            if visual[p.x + (grid.shape[0] * mult), p.y + (grid.shape[1] * mult)] != "#":
                visual[p.x + (grid.shape[0] * mult), p.y + (grid.shape[1] * mult)] = "O"
            else:
                visual[p.x + (grid.shape[0] * mult), p.y + (grid.shape[1] * mult)] = "?"
            max_x = max(max_x, p.x + (grid.shape[0] * mult))
            max_y = max(max_y, p.y + (grid.shape[1] * mult))
            min_x = min(min_x, p.x + (grid.shape[0] * mult))
            min_y = min(min_y, p.y + (grid.shape[1] * mult))
        # except IndexError:
        #     visualize_helper(grid, reachable, side_len + 2)
        #     return
    count = 0
    for w in wrapped_point_sets[step].union(almost_reachable_sets[step]):
        glyph = visual[w.x + (grid.shape[0] * mult), w.y + (grid.shape[1] * mult)]
        if glyph == "O":
            visual[w.x + (grid.shape[0] * mult), w.y + (grid.shape[1] * mult)] = "X"
        elif glyph == "#":
            visual[w.x + (grid.shape[0] * mult), w.y + (grid.shape[1] * mult)] = "@"
            count += 1
        else:
            visual[w.x + (grid.shape[0] * mult), w.y + (grid.shape[1] * mult)] = "!"
    s = to_string(visual[min_x-3:max_x+3, min_y-3:max_y+3])
    print(s)
    print(len([c for c in s if c == "@"]))

cache = {}
def solve(s: str, num_steps: int) -> int:
    grid = numpy.array([[c for c in line] for line in s.splitlines()])
    start = find_start(grid)
    reachable = num_reachable(cache, grid, start, num_steps)
    # visualize(grid, reachable, num_steps)
    # print(num_steps)
    return len(reachable)





# print(solve(example, 20))
# print(solve(input, 64))
import os
import pickle
vals = {}
if os.path.exists("problem21_cache.txt"):
    with open("problem21_cache.txt", "r") as f:
        print("loading cache")
        cache = pickle.load(f)

if os.path.exists("problem21_valcache.txt"):
    with open("problem21_valcache.txt", "r") as f:
        print("loading val cache")
        vals = pickle.load(f)

guesses = []
dist = 60
for i in tqdm(range(0, dist)):
    if i not in vals:
        vals[i] = solve(input, i)

# cache stuff
with open("problem21_cache.txt", "w") as f:
    pickle.dump(cache, f)
with open("problem21_valcache.txt", "w") as f:
    pickle.dump(vals, f)



class GridSearchSpace(SearchSpace[Point, Point]):

    def __init__(self, grid: numpy.ndarray):
        self.grid = grid

    def actions(self, state: State) -> list[Action]:
        actions = []
        for dir in [UP, DOWN, LEFT, RIGHT]:
            new_state = state + dir
            if is_inside(grid, new_state) and self.grid[new_state.x, new_state.y] != "#":
                actions.append(new_state)
        return actions

    def result(self, state: State, action: Action) -> State:
        return action

    def cost(self, state: State, action: Action) -> float:
        return 1

    def states(self) -> list[State]:
        result = []
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                if self.grid[i, j] != "#":
                    result.append(Point(i, j))
        return result

all_dists = all_distance_bfs_search(GridSearchSpace(grid), find_start(grid))

def get_rock_point_count(i: int) -> int:
    if i <= 0:
        return 0
    index = i % grid.shape[0] + grid.shape[0]
    mult = i // grid.shape[0]
    backwards1 = max(i - 1 % grid.shape[0], 0)
    backwards = max(i - 2 % grid.shape[0], 0)
    backwards2 = max(i - 4 % grid.shape[0], 0)

    result = pointcounts[i % grid.shape[0]] + almost_reachable_counts[i % grid.shape[0]] + harder_reachable_counts[i % grid.shape[0]] + harder_reachable_counts[backwards1] - almost_reachable_counts[backwards] - harder_reachable_counts[backwards2] + (wrapped_point_counts[index] + almost_reachable_counts[index] - almost_reachable_counts[index-2]) * (mult)
    return result


# for i in tqdm(range(0, dist)):
#     vals.append(solve(input, i))
#     num_rows = ((i-1)*2+1)
#     num_spaces = num_rows * 2 + 2 + (vals[-3] if len(vals) >= 3 else 0)
#     # print(i, vals[-1], num_rows, num_spaces)
#     guesses.append(num_spaces)

def get_filled_point_count(i: int, prev: int) -> int:
    num_rows = ((i - 1) * 2 + 1)
    num_spaces = num_rows * 2 + 2 + prev
    num_not_rocks = num_spaces - get_rock_point_count(i)
    return num_not_rocks

# prev = 1
# prevprev = 0
# now = 0
# for i in tqdm(range(1,40)):
#     num_rows = ((i - 1) * 2 + 1)
#     num_spaces = num_rows * 2 + 2 + prevprev
#     now = get_filled_point_count(i, prevprev)
#     trueresult = vals[i] if i < len(vals) else 0
#     prevprev = prev
#     prev = now
#     print(i, now, trueresult, num_spaces,  num_spaces - trueresult,  get_rock_point_count(i))
#     # print(i, now, vals[i] if i < len(vals) else None, get_rock_point_count(i), pointcounts[i], almost_reachable_counts[i], almost_reachable_counts[i-2], harder_reachable_counts[i],  harder_reachable_counts[i-2], num_rows * 2 + 2)
# print(now)
# print(almost_reachable_counts)
# print(harder_reachable_counts)

# 618558101920725 is too low

prev = 1
prevprev = 0
now = 0
for i in tqdm(range(1,dist)):
    # num_rows = ((i - 1) * 2 + 1)
    # num_spaces = num_rows * 2 + 2 + prevprev
    now = prevprev + len([k for k in all_dists if all_dists[k] == i % grid.shape[0]])
    trueresult = vals[i] if i < len(vals) else 0
    prevprev = prev
    prev = now
    print(i, now, trueresult)