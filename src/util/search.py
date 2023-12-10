from typing import TypeVar, Protocol, Generic, Callable, Optional
from queue import PriorityQueue

State = TypeVar('State')
Action = TypeVar('Action')


class SearchSpace(Protocol[State, Action]):
    def actions(self, state: State) -> list[Action]:
        ...

    def result(self, state: State, action: Action) -> State:
        ...

    def cost(self, state: State, action: Action) -> float:
        ...

def astar_search(space: SearchSpace[State, Action], start: State, goal: State, heuristic: Callable[[State, Action], float], beam_size: Optional[int] = None) -> list[Action]:
    queue = PriorityQueue()
    queue.put((0, start, []))
    visited = set()
    while not queue.empty():
        _, state, path = queue.get()
        if state == goal:
            return path
        if state in visited:
            continue
        visited.add(state)
        next_elements = []
        for action in space.actions(state):
            new_state = space.result(state, action)
            new_path = path + [action]
            next_elements.append((space.cost(state, action) + heuristic(new_state, action), new_state, new_path))
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

class AdjacentMatrixSearchSpace(Generic[State], SearchSpace[State, State]):
    def __init__(self, matrix: dict[State, list[State]]):
        self.matrix = matrix

    def actions(self, state: State) -> list[State]:
        return self.matrix[state]

    def result(self, state: State, action: State) -> State:
        return action

    def cost(self, state: State, action: State) -> float:
        return 1


if __name__ == "__main__":
    g = {
        1: [2, 3],
        2: [1, 4],
        3: [1, 4],
        4: [2, 3, 5],
        5: [4, 6],
        6: [7],
        7: [6, 8, 9],
        8: [1],
        9: [3]
    }

    space = AdjacentMatrixSearchSpace(g)
    print(astar_search(space, 1, 9, lambda s, a: 0))