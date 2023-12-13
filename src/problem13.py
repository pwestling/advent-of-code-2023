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

input = resource("problem13.txt")
example = """#.##..##.
..#.##.#.
##......#
##......#
..#.##.#.
..##..##.
#.#.##.#.

#...##..#
#....#..#
..##..###
#####.##.
#####.##.
..##..###
#....#..#"""


def do_check(nums: list[int]) -> int:
    for i in range(1, len(nums)):
        front = nums[:i]
        back = nums[i:]
        shorter = min(len(front), len(back))
        front.reverse()
        front = front[:shorter]
        back = back[:shorter]
        # print(i, front, back)
        if front == back:
            return i
    return -1

def solve_one(s: str) -> int:
    grid = Grid(s.split("\n"))
    # for each grid row create a binary number based on where # are
    nums = []
    for i in range(grid.max_x):
        nums.append(sum(2**j for j, x in enumerate(grid.get_row(i)) if x == "#"))

    horizontal = do_check(nums)
    if horizontal > 0:
        return horizontal * 100

    # try vertical rows
    nums = []
    for i in range(grid.max_y):
        nums.append(sum(2**j for j, x in enumerate(grid.get_col(i)) if x == "#"))

    vertical = do_check(nums)
    return vertical

def solve(s: str) -> int:
    # split the input by empty rows
    rows = s.split("\n\n")
    return sum(solve_one(row) for row in rows)

# print(solve_one(example.split("\n\n")[1]))
# print(solve_one(example.split("\n\n")[0]))
# print(solve(example))

# with timed():
#     print(solve(input))

def do_check_two(nums: list[int]) -> int:
    solutions = []
    for i in range(len(nums)):
        front = nums[:i]
        back = nums[i:]
        shorter = min(len(front), len(back))
        front.reverse()
        front = front[:shorter]
        back = back[:shorter]
        diffs = []
        # print("fb", i, front, back)
        for k in range(len(front)):
            diff = front[k] ^ back[k]
            if diff != 0:
                diffs.append(diff)
        if len(diffs) == 1:
            if math.log(diffs[0], 2).is_integer():
                # print(front, back, diffs, i)
                solutions.append(i)
            else:
                # print("Not power of 2", diffs[0])
                pass
    if len(solutions) == 1:
        return solutions[0]
    elif len(solutions) > 1:
        print("Multiple solutions", solutions)
        raise Exception("Multi solution")
    return -1

def solve_single_two(s: str) -> int:
    grid = Grid(s.split("\n"))
    # for each grid row create a binary number based on where # are
    # print("try vert")
    # try vertical rows
    nums = []
    for i in range(grid.max_y):
        nums.append(sum(2**j for j, x in enumerate(grid.get_col(i)) if x == "#"))
    # print("Nums", nums)

    vertical = do_check_two(nums)

    # print("try horiz")

    nums = []
    for i in range(grid.max_x):
        nums.append(sum(2 ** j for j, x in enumerate(grid.get_row(i)) if x == "#"))
    # print("Nums",nums)
    horizontal = do_check_two(nums)

    if vertical >= 0 and horizontal >= 0:
        print(s)
        print(vertical, horizontal)
        raise Exception("No solution")

    if vertical >= 0:
        # print("vertical", vertical)
        return vertical

    if horizontal >= 0:
        # print("horizontal", horizontal)
        return horizontal * 100

    print(s)
    raise Exception("No solution")

def solve2(s: str) -> int:
    # split the input by empty rows
    rows = s.strip().split("\n\n")
    results = [solve_single_two(row) for row in rows]
    return sum(results)

# print(solve_single_two(example.split("\n\n")[1]))
# print(solve_single_two(example.split("\n\n")[0]))

if solve2(example) != 400:
    print("Example Wrong " + str(solve2(example)))
    exit(1)


example2 = """
#..#
.##.
.#..
....
"""

# print("Doing example 2")
# print(solve2(example2))

example3 = """#.#.##..#..
#.....#.###
#####.##.##
#.####.....
##..###....
#...#...#..
##...###.#.
.#.######..
.#.######.."""

print("Doing example 3")
print(solve2(example3))

example4 = """
.##...###
#..#.#..#
...#.#..#
##.##....
######..#
######..#
##.##...."""

print("Doing example 4")
print(solve2(example4))

print(solve2(input))
# incorrect: 33253 26058 26162 33432 33438


