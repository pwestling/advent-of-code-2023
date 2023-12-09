import math
import time
from dataclasses import dataclass
from typing import Optional

from util.resources import resource
from parsec import *

input = resource("problem8.txt")
example = """RL

AAA = (BBB, CCC)
BBB = (DDD, EEE)
CCC = (ZZZ, GGG)
DDD = (DDD, DDD)
EEE = (EEE, EEE)
GGG = (GGG, GGG)
ZZZ = (ZZZ, ZZZ)"""

example2 = """LLR

AAA = (BBB, BBB)
BBB = (AAA, ZZZ)
ZZZ = (ZZZ, ZZZ)"""

example3 = """LR

11A = (11B, XXX)
11B = (XXX, 11Z)
11Z = (11B, XXX)
22A = (22B, XXX)
22B = (22C, 22C)
22C = (22Z, 22Z)
22Z = (22B, 22B)
XXX = (XXX, XXX)"""


def to_dict(s: str) -> dict[str, tuple[str,str]]:
    lines = s.split("\n")[2:]
    d: dict[str, str] = {}
    for line in lines:
        if line.strip():
            key, value = line.split(" = ")
            values = value[1:-1].split(", ")
            d[key] = (values[0], values[1])
    return d

print(to_dict(example))

def solve(input: str) -> int:
    steps = input.split("\n")[0]
    d = to_dict(input)
    current = "AAA"
    count = 0
    while current != "ZZZ":
        instruction = steps[count % len(steps)]
        count += 1
        if instruction == "R":
            current = d[current][1]
        else:
            current = d[current][0]
    return count

print(solve(example))

print(solve(example2))
print(solve(input))

def lcm(a: int, b: int) -> int:
    return abs(a*b) // math.gcd(a, b)

def solve2(input: str) -> int:
    steps = input.split("\n")[0]
    d = to_dict(input)
    start_nodes = [k for k in d.keys() if k.endswith("A")]
    print(start_nodes)
    node_periods = {}
    for node in start_nodes:
        current = node
        count = 0
        while not current.endswith("Z"):
            instruction = steps[count % len(steps)]
            count += 1
            if instruction == "R":
                current = d[current][1]
            else:
                current = d[current][0]
        node_periods[node] = count
    x = 1
    for v in node_periods.values():
        x = lcm(x, v)
    return x

print(solve2(example3))
print(solve2(input))