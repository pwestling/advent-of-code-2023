import functools
import math
import time
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
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

input = resource("problem20.txt")

example = """broadcaster -> a, b, c
%a -> b
%b -> c
%c -> inv
&inv -> a"""

class PulseStrength(Enum):
    LOW = 1
    HIGH = 2

class ComponentType(Enum):
    BROADACST = "BROADCAST"
    CONJUNCTION = "CONJUNCTION"
    FLIPFLOP = "FLIPFLOP"
    UNTYPED = "UNTYPED"

    def __str__(self):
        return self.name

@dataclass
class Component:
    name: str
    type: ComponentType
    dests: list[str]
    memory: dict[str, PulseStrength]
    onoff: bool
    state_sequence: "list[tuple[dict[str, PulseStrength], bool]]"
    time_to_low: int
    time_to_high: int
    parents: "list[Component]"
    sent_this_run: Optional[PulseStrength] = None

    # def capture_state(self):
    #     state = (self.memory.copy(), self.onoff)
    #     if self.time_to_cycle == -1 and all(p.time_to_cycle != -1 for p in self.parents):
    #         if state in self.state_sequence:
    #
    #     self.state_sequence.append(state)


def parse_component(s :str) -> Component:
    parts = s.split("->")
    name = parts[0].strip()
    dests = [s.strip() for s in parts[1].split(",")]
    if s.startswith("%"):
        return Component(name[1:], ComponentType.FLIPFLOP, dests, {}, False, [], -1, -1, [])
    elif s.startswith("&"):
        return Component(name[1:], ComponentType.CONJUNCTION, dests, {}, False, [], -1, -1, [])
    elif name == "broadcaster":
        return Component(name, ComponentType.BROADACST, dests, {}, False, [], -1, -1, [])
    else:
        raise Exception("Invalid component")


def parse(s: str) -> dict[str, Component]:
    compmap =  {c.name: c for c in map(parse_component, s.split("\n"))}
    for c in list(compmap.values()):
        for d in c.dests:
            if d not in compmap:
                compmap[d] = Component(d, ComponentType.UNTYPED, [], {}, False, [], -1, -1, [])

    for c in compmap.values():
        for c2 in compmap.values():
            if c.name in c2.dests:
                c.parents.append(c2.name)
    return compmap



@dataclass
class PulseResults:
    high: int
    low: int
    rx_triggered: bool = False

    def __add__(self, other):
        return PulseResults(self.high + other.high, self.low + other.low, other.rx_triggered or self.rx_triggered)

def do_append(source: Component, queue: list[tuple[Component, PulseStrength, str]], components: dict[str, Component], dest: str, strength: PulseStrength):
    source.sent_this_run = strength
    if dest in components:
        c = components[dest]
        queue.append((c, strength, source.name))
    else:
        queue.append((None, strength, source.name))
        # print(f"{source.name} {strength} -> {c.name}")

def run(components: dict[str, Component]) -> PulseResults:
    results = PulseResults(0,0)
    for c in components.values():
        c.sent_this_run = None
        for d in c.dests:
            if d in components and components[d].type == ComponentType.CONJUNCTION:
                components[d].memory[c.name] = PulseStrength.LOW

    queue = [(components["broadcaster"], PulseStrength.LOW, "button")]
    while queue:
        c, strength, source = queue.pop(0)
        if strength == PulseStrength.HIGH:
            results.high += 1
        else:
            results.low += 1
        if c is None:
            continue
        if c.type == ComponentType.BROADACST:
            for d in c.dests:
                do_append(c, queue, components, d, strength)
        elif c.type == ComponentType.CONJUNCTION:
            c.memory[source] = strength
            if all(v == PulseStrength.HIGH for v in c.memory.values()):
                for d in c.dests:
                    do_append(c, queue, components, d, PulseStrength.LOW)
            else:
                for d in c.dests:
                    do_append(c, queue, components, d, PulseStrength.HIGH)
        elif c.type == ComponentType.FLIPFLOP:
            if strength == PulseStrength.LOW:
                if c.onoff == True:
                    c.onoff = False
                    for d in c.dests:
                        do_append(c, queue, components, d, PulseStrength.LOW)
                else:
                    c.onoff = True
                    for d in c.dests:
                        do_append(c, queue, components, d, PulseStrength.HIGH)

    return results

def do_append2(source: Component, queue: list[tuple[Component, PulseStrength, str]], components: dict[str, Component], dest: str, strength: PulseStrength):
    if dest in components:
        c = components[dest]
        queue.append((c, strength, source.name))
    else:
        queue.append((None, strength, source.name))
        # print(f"{source.name} {strength} -> {c.name}")

def lcm(nums: list[int]) -> int:
    result = 1
    for n in nums:
        result = result * n // math.gcd(result, n)
    return result

def run_multi(components: dict[str, Component]) -> int:
    for c in components.values():
        for d in c.dests:
            if d in components and components[d].type == ComponentType.CONJUNCTION:
                components[d].memory[c.name] = PulseStrength.LOW

    components["broadcaster"].time_to_low = 1
    components["broadcaster"].time_to_high = math.inf

    while components["rx"].time_to_low == -1:
        changed = False
        for component in components.values():
            if component.type == ComponentType.FLIPFLOP and ([
                    components[p].type == ComponentType.CONJUNCTION for p in component.parents].count(True) > 0 ):
                print("FLAG", component.name, component.parents)
            parent_low_signals = [components[p].time_to_low for p in component.parents if components[p].time_to_low != -1]
            parent_high_signals = [components[p].time_to_high for p in component.parents if components[p].time_to_high != -1]
            named_signals = [(p, components[p].type, components[p].time_to_low, components[p].time_to_high) for p in component.parents]
            if component.type == ComponentType.FLIPFLOP:
                if len(parent_low_signals) > 0 and component.time_to_low == -1:
                    lowes_count = min(parent_low_signals)
                    component.time_to_low = lowes_count * 2
                    component.time_to_high = lowes_count
                    changed = True
                    print("changed low flipflop", component.name, "to", component.time_to_low, named_signals)
            elif component.type == ComponentType.CONJUNCTION:
                if len(parent_high_signals) == len(component.parents) and len(parent_low_signals) == len(component.parents) and component.time_to_low == -1:
                    print("Calcing low conj", component.name, "from", parent_high_signals, component.parents)
                    # mult = lcm(parent_high_signals)
                    # result = mult
                    # while [result % components[p].time_to_low >= components[p].time_to_high for p in component.parents if components[p].time_to_low != -1].count(True) > 0:
                    #     result += mult
                    result = 1
                    for p in component.parents:
                        result *= components[p].time_to_high
                    component.time_to_low = result
                    changed = True
                    print("changed low conj", component.name, "to", component.time_to_low, named_signals)
                if len(parent_low_signals) > 0 and component.time_to_high == -1:
                    component.time_to_high = min(parent_low_signals + parent_high_signals)
                    changed = True
                    print("changed high conj", component.name, "to", component.time_to_high, named_signals)
            elif component.type == ComponentType.UNTYPED:
                if len(parent_low_signals) > 0:
                    component.time_to_low = max([components[p].time_to_low for p in component.parents])
                    changed = True
                    print("changed", component.name, "to", component.time_to_low, named_signals)
            elif component.type == ComponentType.BROADACST:
                continue
        if not changed:
            raise Exception("No change")
    return components["rx"].time_to_low


def run1k(components: dict[str, Component]) -> int:
    result = PulseResults(0,0)
    for i in range(1000):
        result += run(components)
    return result.high * result.low

def runN(components: dict[str, Component], n: int, target: str, exclude: set[str]) -> Optional[PulseStrength]:
    result = PulseResults(0,0)
    for i in tqdm(range(n)):
        result += run(components)
        for c in components.values():
            if c.name not in exclude:
                if c.sent_this_run == PulseStrength.LOW and c.type == ComponentType.CONJUNCTION:
                    print(i+1, c.name, c.sent_this_run)
    return components[target].sent_this_run

class ComponentSearchSpace(SearchSpace[str, str]):
    def __init__(self, components: dict[str, Component]):
        self.components = components

    def actions(self, state: str) -> list[str]:
        if state in self.components:
            return self.components[state].dests
        else:
            return []

    def result(self, state: str, action: str) -> str:
        return action

    def cost(self, state: str, action: str) -> float:
        return 1





def run_to_rx(components: dict[str, Component]) -> int:

    all_paths_to_rx = bfs_search(ComponentSearchSpace(components), "broadcaster", "rx")
    print(all_paths_to_rx)
    for c in all_paths_to_rx:
        if c in components:
            print(components[c])



    count = 0
    while True:
        result = run(components)
        count += 1
        if count % 10000 == 0:
            print(count)
        if result.rx_triggered:
            return count

# print(parse(example))
# print(run(parse(example)))
# print(run1k(parse(example)))
# print(run1k(parse(input)))

print(run_multi(parse(input)))
# print(runN(parse(input), 40, "kr", {"tx", "nd", "pc", "vd"}))

for x in [2048, 8, 256, 512, 1024, 32, 1]:
    print(70368744177664 % (2*x))
