import math
import time
from dataclasses import dataclass
from typing import Optional

from util.resources import resource
from parsec import *

input = resource("problem9.txt")
example = """0 3 6 9 12 15
1 3 6 10 15 21
10 13 16 21 30 45"""

def get_seq_next(nums: list[int]) -> int:

    if set(nums) == {0}:
        return 0
    else:
        diffs = [nums[i+1] - nums[i] for i in range(len(nums)-1)]
        return nums[-1] + get_seq_next(diffs)

print(get_seq_next([0,3,6,9,12,15]))
print(get_seq_next([1,3,6,10,15,21]))

def solve(input: str) -> int:
    lines = input.split("\n")
    k = 0
    for l in lines:
        nums = [int(x) for x in l.split(" ") if x.strip()]
        k += get_seq_next(nums)
    return k

print(solve(example))
print(solve(input))

def get_seq_first(nums: list[int]) -> int:

    if set(nums) == {0}:
        return 0
    else:
        diffs = [nums[i+1] - nums[i] for i in range(len(nums)-1)]
        return nums[0] - get_seq_first(diffs)

def solve2(input: str) -> int:
    lines = input.split("\n")
    k = 0
    for l in lines:
        nums = [int(x) for x in l.split(" ") if x.strip()]
        k += get_seq_first(nums)
    return k

print(get_seq_first([10,13,16,21,30,45]))
print(solve2(example))
print(solve2(input))


