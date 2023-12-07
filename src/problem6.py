import math
import time
from dataclasses import dataclass
from typing import Optional

from util.resources import resource
from parsec import *

input = resource("problem6.txt")
example = """Time:      7  15   30
Distance:  9  40  200"""

def vals(s: str) -> list[int]:
    return [int(x) for x in s.split(": ")[1].split(" ") if x.strip()]

def parse(s: str) -> list[tuple[int, int]]:
    lines = s.split("\n")
    times = vals(lines[0])
    dists = vals(lines[1])
    return list(zip(times, dists))

def find_ways(time: int, dist: int):
    count = 0
    for i in range(1, time+1):
        distance_traveled = (i * (time-i))
        if distance_traveled > dist:
            count += 1
    return count

def solve(input: str) -> int:
    lines = parse(input)
    total = 1
    for time, dist in lines:
        total *= find_ways(time, dist)
    return total

print(solve(example))
print(solve(input))

def val(s: str) -> int:
    return int("".join([x for x in s.split(": ")[1].split(" ") if x.strip()]))


def parse_2(s: str) -> tuple[int, int]:
    lines = s.split("\n")
    time = val(lines[0])
    dist = val(lines[1])
    return time, dist

def solve2(input: str) -> int:
    time, dist = parse_2(input)
    total = find_ways(time, dist)
    return total

print(solve2(example))
print(solve2(input))