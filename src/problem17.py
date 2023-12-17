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

input = resource("problem17.txt")
example = """2413432311323
3215453535623
3255245654254
3446585845452
4546657867536
1438598798454
4457876987766
3637877979653
4654967986887
4564679986453
1224686865563
2546548887735
4322674655533"""

def best_path(grid: np.ndarray, visual_grid: np.ndarray, cache: dict, start: Point, direction: Point, path_length: int, loss: int, depth: int, best_loss_global: list[int]) -> int:

    heat_loss = grid[start.x, start.y]
    # print("heat loss", heat_loss)
    if (start, direction) in cache:
        if cache[(start, direction)] < loss:
            # print("pruning because of cache hit", start, direction, cache[(start, direction)], loss)
            return math.inf
    cache[(start, direction)] = loss
    # print(cache)

    if start.x == grid.shape[0] - 1 and start.y == grid.shape[1] - 1:
        if loss + heat_loss < best_loss_global[0]:
            best_loss_global[0] = loss + heat_loss
            print("new best loss", best_loss_global[0])
        print("found solution", loss + heat_loss)
        return loss + heat_loss

    if loss > best_loss_global[0]:
        # print("pruning")
        return math.inf

    # if (start, direction) in cache:
    #     print("cache hit")
    #     return cache[(start, direction, path_length)]


    visual_grid[start.x, start.y] = "*"
    # print(visual_grid)
    if direction == UP:
        visual_grid[start.x, start.y] = "^"
    elif direction == DOWN:
        visual_grid[start.x, start.y] = "v"
    elif direction == LEFT:
        visual_grid[start.x, start.y] = "<"
    elif direction == RIGHT:
        visual_grid[start.x, start.y] = ">"
    # print(depth)

    possible_directions = [direction.turn_right(), direction.turn_left()]
    if path_length < 3:
        possible_directions = [direction] + possible_directions

    best_loss = None
    for dir in possible_directions:
        new_segment_length = (path_length + 1 if dir == direction else 1)
        if is_inside(grid, start + dir):
            new_loss = best_path(grid, visual_grid, cache, start + dir, dir,new_segment_length, loss + heat_loss, depth + 1, best_loss_global)
            if best_loss is None or new_loss < best_loss:
                best_loss = new_loss
    if best_loss is None:
        raise Exception("no best loss")
    # cache[(start, direction)] = best_loss
    return best_loss


@dataclass
class SearchState:
    position: Point
    direction: Point
    path_length: int
    loss: int

    def to_tuple(self):
        return (self.position, self.direction, self.path_length)
    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

    def __lt__(self, other):
        return self.loss < other.loss

class NumGridSearchSpace(SearchSpace[SearchState, Point]):

    def __init__(self, grid: np.ndarray, heuristic: Callable[[SearchState, Point], float] = None):
        self.grid = grid
        self.heuristic = heuristic

    def actions(self, state: SearchState) -> list[Point]:
        possible_directions = [state.direction.turn_right(), state.direction.turn_left()]
        if state.path_length < 3:
            possible_directions = [state.direction] + possible_directions

        return [p for p in possible_directions if is_inside(self.grid, state.position + p)]

    def result(self, state: SearchState, action: Point) -> SearchState:
        return SearchState(
            state.position + action,
            action,
            state.path_length + 1 if action == state.direction else 1,
            self.cost(state, action))

    def cost(self, state: SearchState, action: Point) -> float:
        return state.loss + float(self.grid[state.position.x + action.x, state.position.y + action.y])

    def states(self) -> list[SearchState]:
        return []


import sys
sys.setrecursionlimit(4000)

def as_grid(grid: np.ndarray) -> str:
    return "\n".join("".join(str(x) for x in row) for row in grid)

def visualize(grid: np.ndarray, path: list[Point]) -> int:
    visual_grid = grid.copy()
    current = Point(0, 0)
    sum = 0
    for p in path:
        current = current + p
        sum += int(grid[current.x, current.y])
        if p == UP:
            visual_grid[current.x, current.y] = "^"
        elif p == DOWN:
            visual_grid[current.x, current.y] = "v"
        elif p == LEFT:
            visual_grid[current.x, current.y] = "<"
        elif p == RIGHT:
            visual_grid[current.x, current.y] = ">"

    print(as_grid(visual_grid))
    return sum

def solve(s: str) -> int:
    toint = np.vectorize(int)
    grid = to_numpy(s)
    intgrid = toint(grid.copy())
    start = SearchState(Point(0, 0), RIGHT, 0, 0)
    start_cost = intgrid[0, 0]
    end = Point(grid.shape[0] - 1, grid.shape[1] - 1)
    end_state = SearchState(end, LEFT, 1, 0)
    end_cost = intgrid[end.x, end.y]
    def is_end(state: SearchState) -> bool:
        return state.position == end

    def heuristic_stupid(state: SearchState, direction: Point) -> float:
        return 0
    def heuristic_simple(state: SearchState, direction: Point) -> float:
        dist = end - state.position
        return abs(dist.x) + abs(dist.y)

    def heuristic_start(state: SearchState, direction: Point) -> float:
        dist_p = end - state.position
        dist = abs(dist_p.x) + abs(dist_p.y)
        # find the smallest "dist" points in the space between here and the end, and sum their losses
        losses = []
        for i in range(state.position.x, end.x + 1):
            for j in range(state.position.y, end.y + 1):
                losses.append(intgrid[i, j])
        losses.sort()
        losses = losses[:dist]
        return sum(losses)

    print("Min cost", heuristic_start(start, RIGHT))

    space = NumGridSearchSpace(intgrid)
    cost, path = astar_search(space, start, is_end, heuristic_simple)
    print(cost)
    result = visualize(grid, path)
    print("Cost", cost)

    return cost

with timed():
    x = solve(example)
    if x != 102:
        raise Exception("wrong answer on example")

with timed():
    print(solve(input))

# 1212 too high
# 1178 not correct
# 1125 not correct

