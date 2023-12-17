from dataclasses import dataclass
from typing import TypeVar, Generic, Iterable, Optional, Callable, cast

import numpy
import numpy as np
import sys
sys.setrecursionlimit(6000)

@dataclass
class Point:
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def step_up(self):
        return self + UP

    def step_down(self):
        return self + DOWN

    def step_left(self):
        return self + LEFT

    def step_right(self):
        return self + RIGHT

    def turn_left(self):
        if self == UP:
            return LEFT
        elif self == DOWN:
            return RIGHT
        elif self == LEFT:
            return DOWN
        elif self == RIGHT:
            return UP

    def turn_right(self):
        return self.turn_left().turn_left().turn_left()

    def __repr__(self):
        if self == UP:
            return "UP"
        elif self == DOWN:
            return "DOWN"
        elif self == LEFT:
            return "LEFT"
        elif self == RIGHT:
            return "RIGHT"
        return f"Point({self.x}, {self.y})"

    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)


UP = Point(-1, 0)
DOWN = Point(1, 0)
LEFT = Point(0, -1)
RIGHT = Point(0, 1)

def add_point(p: Point, d: Point) -> Point:
    return Point(p.x + d.x, p.y + d.y)

T = TypeVar("T")
class Grid(Generic[T]):

    def __init__(self, grid: Iterable[Iterable[T]]):
        self.grid = list(list(x) for x in grid)
        self.max_y = len(self.grid[0])
        self.max_x = len(self.grid)

    def __getitem__(self, p: Point) -> T:
        return self.grid[p.x][p.y]

    def get(self, p: Point) -> Optional[T]:
        if 0 <= p.x < self.max_x and 0 <= p.y < self.max_y:
            return self.grid[p.x][p.y]
        else:
            return None

    def is_inside(self, p: Point) -> bool:
        return 0 <= p.x < self.max_x and 0 <= p.y < self.max_y

    def __setitem__(self, p: Point, value: T):
        self.grid[p.x][p.y] = value

    def set(self, p: Point, value: T):
        self.grid[p.x][p.y] = value

    def copy(self) -> "Grid[T]":
        grid_copy = []
        for row in self.grid:
            grid_copy.append(row.copy())
        return Grid(grid_copy)

    def points(self) -> Iterable[Point]:
        for i in range(self.max_x):
            for j in range(self.max_y):
                yield Point(i, j)

    def points_where(self, predicate: Callable[[T], bool]) -> list[Point]:
        result = []
        for i in range(self.max_x):
            for j in range(self.max_y):
                if predicate(self.grid[i][j]):
                    result.append(Point(i, j))
        return result

    def as_adjacency_list(self, is_valid: Optional[Callable[[Point], bool]] = None) -> dict[Point, list[Point]]:
        if is_valid is None:
            is_valid = lambda p: True
        result = {}
        for p in self.points():
            if is_valid(p):
                result[p] = []
                for d in [UP, DOWN, LEFT, RIGHT]:
                    if is_valid(p + d) and self.is_inside(p + d):
                        result[p].append(p + d)
        return result

    def __str__(self):
        return "\n".join("".join(str(x) for x in row) for row in self.grid)

    def get_row(self, i: int) -> list[T]:
        return self.grid[i]

    def get_col(self, j: int) -> list[T]:
        return [row[j] for row in self.grid]

K = TypeVar("K")
def flood_fill(g: Grid[K], start: Point, is_valid: Optional[Callable[[Point], bool]] = None) -> Grid[bool]:
    if is_valid is None:
        is_valid = lambda p: True
    visited = Grid([[False for _ in range(g.max_y)] for _ in range(g.max_x)])
    queue = [start]
    while queue:
        p = queue.pop(0)
        if not visited[p] and is_valid(p):
            visited[p] = True
            for d in [UP, DOWN, LEFT, RIGHT]:
                queue.append(p + d)
    return visited


def to_numpy(s: str) -> np.ndarray:
    return np.array([[c for c in row] for row in s.split("\n") if row.strip()])

def is_inside(grid: np.ndarray, p: Point) -> bool:
    return 0 <= p.x < grid.shape[0] and 0 <= p.y < grid.shape[1]