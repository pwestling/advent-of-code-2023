from dataclasses import dataclass
from typing import TypeVar, Protocol, Generic, Callable, Optional
from queue import PriorityQueue
import math

from tqdm import tqdm

State = TypeVar('State')
Action = TypeVar('Action')


class SearchSpace(Protocol[State, Action]):
    def actions(self, state: State) -> list[Action]:
        ...

    def result(self, state: State, action: Action) -> State:
        ...

    def cost(self, state: State, action: Action) -> float:
        ...

    def states(self) -> list[State]:
        ...

def astar_search(space: SearchSpace[State, Action], start: State, is_goal: Callable[[State], bool], heuristic: Callable[[State, Action], float], beam_size: Optional[int] = None, expected_max: float = None) -> tuple[float, list[Action]]:
    queue = PriorityQueue()
    queue.put((0, start, []))
    best_scores = {}
    highest_cost = 0
    while not queue.empty():
        this_cost, state, path = queue.get()
        if this_cost > highest_cost:
            highest_cost = this_cost
        # print(this_cost, state, path)
        if is_goal(state):
            return this_cost, path
        # if state in visited:
        #     continue
        # visited.add(state)
        next_elements = []
        for action in space.actions(state):
            new_state = space.result(state, action)
            new_path = path + [action]
            cost = space.cost(state, action)
            # if new_state in best_scores:
            #     print("found", new_state, best_scores[new_state], cost)
            if best_scores.get(new_state, math.inf) > cost:
                # print(len(best_scores))
                best_scores[new_state] = cost
                next_elements.append((cost + heuristic(new_state, action), new_state, new_path))
        if beam_size is not None:
            next_elements.sort(key=lambda x: x[0])
            next_elements = next_elements[:beam_size]
        for element in next_elements:
            queue.put(element)

def all_distance_bfs_search(space: SearchSpace[State, Action], start: State) -> dict[State, int]:
    queue = [(0, start)]
    visited = set()
    result = {}
    while queue:
        cost, state = queue.pop(0)
        if state in visited:
            continue
        visited.add(state)
        result[state] = cost
        for action in space.actions(state):
            new_state = space.result(state, action)
            new_cost = cost + space.cost(state, action)
            queue.append((new_cost, new_state))
    return result

def bfs_search(space: SearchSpace[State, Action], start: State, goal: State) -> list[Action]:
    queue = [(start, [])]
    visited = set()
    while queue:
        state, path = queue.pop(0)
        if state == goal:
            return path
        if state in visited:
            continue
        visited.add(state)
        for action in space.actions(state):
            new_state = space.result(state, action)
            new_path = path + [action]
            queue.append((new_state, new_path))
@dataclass
class FloydWarshallResult:
    distance: dict[State, dict[State, float]]
    next: dict[State, dict[State, State]]

    def path(self, start: State, end: State) -> list[State]:
        return self.path_recur(self.next[start][end], end)

    def path_recur(self, start: State, end: State) -> list[State]:
        if self.next[start][end] is None:
            return [end]
        else:
            return [start] + self.path_recur(self.next[start][end], end)

def floyd_warshall_search(space: SearchSpace[State, Action]) -> FloydWarshallResult:
    distance = {}
    next = {}
    for state in space.states():
        distance[state] = {}
        next[state] = {}
        for state2 in space.states():
            distance[state][state2] = math.inf
            next[state][state2] = None
        distance[state][state] = 0
        for action in space.actions(state):
            state2 = space.result(state, action)
            distance[state][state2] = space.cost(state, action)
            next[state][state2] = state2
    for state in space.states():
        for state2 in space.states():
            for state3 in space.states():
                if distance[state2][state3] > distance[state2][state] + distance[state][state3]:
                    distance[state2][state3] = distance[state2][state] + distance[state][state3]
                    next[state2][state3] = next[state2][state]
    return FloydWarshallResult(distance, next)

def find_all_paths(space: SearchSpace[State, Action], start: State, goal: State) -> list[list[Action]]:
    result = []
    queue = [(start, [])]
    while queue:
        print(len(queue))
        state, path = queue.pop(0)
        if state == goal:
            result.append(path)
        for action in space.actions(state):
            new_state = space.result(state, action)
            new_path = path + [action]
            queue.append((new_state, new_path))
    return result


class AdjacentMatrixSearchSpace(Generic[State], SearchSpace[State, State]):
    def __init__(self, matrix: dict[State, list[State]]):
        self.matrix = matrix

    def actions(self, state: State) -> list[State]:
        return self.matrix[state]

    def result(self, state: State, action: State) -> State:
        return action

    def cost(self, state: State, action: State) -> float:
        return 1

    def states(self) -> list[State]:
        return list(self.matrix.keys())


# if __name__ == "__main__":
#     g = {
#         1: [2, 3],
#         2: [1, 4],
#         3: [1, 4],
#         4: [2, 3, 5],
#         5: [4, 6],
#         6: [7],
#         7: [6, 8, 9],
#         8: [1],
#         9: [3]
#     }
#
#     space = AdjacentMatrixSearchSpace(g)
#     print(astar_search(space, 1, 9, lambda s, a: 0))
#     fw = floyd_warshall_search(space)
#     print(fw.distance[1][9])
#     print(fw.path(1, 9))