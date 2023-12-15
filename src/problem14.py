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

input = resource("problem14.txt")
example = """O....#....
O.OO#....#
.....##...
OO.#O....O
.O.....O#.
O.#..O.#.#
..O..#O..O
.......O..
#....###..
#OO..#...."""

def roll_north(grid: np.ndarray, i: int, j: int) -> np.ndarray:
    # roll north
    k = i
    grid[i, j] = "X"
    grid[i, j] = "O"

    while k >= 1:
        if grid[k-1, j] == ".":
            k -= 1
        else:
            break
    grid[i, j] = "."
    grid[k, j] = "O"
    return grid

def solve(grid: np.ndarray) -> int:
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if grid[i, j] == "O":
                grid = roll_north(grid, i, j)
    return get_load(grid)


def get_load(grid):
    sum = 0
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if grid[i, j] == "O":
                sum += grid.shape[0] - i
    return sum


print(solve(to_numpy(example)))
print(solve(to_numpy(input)))

def as_grid(grid: np.ndarray) -> str:
    return "\n".join("".join(str(x) for x in row) for row in grid)

def num_os(grid: np.ndarray) -> int:
    return sum(1 for x in grid.flatten() if x == "O")

def solve2(s: str, length: int) -> int:
    grid = to_numpy(s)
    grid, cycle_length, cycle_start, cycle_content = find_cycle_stats(grid, length)
    remaining = length - cycle_start
    leftover = remaining % cycle_length
    result = cycle_content[-1*(leftover-1)][1]

    return result


def find_cycle_stats(grid, length):
    sequence = []
    states = set()
    for i in range(length):
        grid = do_cycle(grid)
        sequence = [(as_grid(grid), get_load(grid))] + sequence
        if as_grid(grid) in states:
            cycle_start = i
            for k in range(1,len(sequence)):
                if sequence[k] == sequence[0]:
                    cycle_length = k
                    break
            return grid, cycle_length, cycle_start, sequence[:k]
        states.add(as_grid(grid))

        # for k in range(1, len(sequence) // 4):
        #     if sequence[:k] == sequence[k:2 * k] == sequence[2 * k:3 * k] == sequence[3 * k:4 * k]:
        #         cycle_length = k
        #         cycle_start = i
        #         return grid, cycle_length, cycle_start, sequence[:k]


def do_cycle(grid):
    solve(grid)
    grid = numpy.rot90(grid, -1)
    solve(grid)
    grid = numpy.rot90(grid, -1)
    solve(grid)
    grid = numpy.rot90(grid, -1)
    solve(grid)
    grid = numpy.rot90(grid, -1)
    return grid


print(solve2(example, 1000000000))
with timed():
    print(solve2(input, 1000000000))