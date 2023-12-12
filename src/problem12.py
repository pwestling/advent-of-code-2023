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

input = resource("problem12.txt")
example = """???.### 1,1,3
.??..??...?##. 1,1,3
?#?#?#?#?#?#?#? 1,3,1,6
????.#...#... 4,1,1
????.######..#####. 1,6,5
?###???????? 3,2,1"""

exampleshort = """???.### 1,1,3"""
exampletwo = """.??..??...?##. 1,1,3"""
examplesix = """?###???????? 3,2,1"""


@dataclass
class Row:
    springs: str
    encoding: list[int]

    def __hash__(self):
        return hash((self.springs, tuple(self.encoding)))

    def mult5(self):
        s = []
        for i in range(5):
            s.append(self.springs)
        return Row("?".join(s), self.encoding*5)


def parse(s: str) -> Row:
    parts = s.split(" ")
    return Row(parts[0], [int(x) for x in parts[1].split(",")])


@functools.cache
def get_encoding(row: Row) -> list[int]:
    group_start = None
    groups = []
    q_index = row.springs.find("?")
    alt_sprints = row.springs[:q_index] if q_index != -1 else row.springs
    for i in range(len(alt_sprints)):
        if alt_sprints[i] == "#" and group_start is None:
            group_start = i
        if alt_sprints[i] == "." and group_start is not None:
            groups.append(i - group_start)
            group_start = None
    if group_start is not None and q_index == -1:
        groups.append(len(alt_sprints) - group_start)
    return groups


def is_valid(row: Row) -> bool:
    groups = get_encoding(row)
    return groups == row.encoding


cache = {}
debug_cache = {}

def num_questions(row: Row) -> int:
    return len([c for c in row.springs if c == "?"])

def grog_could_be_valid(row: Row) -> bool:
    encoding = get_encoding(row)
    prefix = row.encoding[:len(encoding)]
    is_valid = True
    for i in range(len(prefix)):
        if prefix[i] == encoding[i] or (prefix[i] >= encoding[i] and i == len(prefix)-1):
            pass
        else:
            is_valid = False
    return is_valid

def valid_permutations_for_row_grog(row: Row, index: int, group_num: int, group_index: int) -> int:
    if index >= len(row.springs)-1 or row.springs[index] != "?" or group_num >= len(row.encoding):
        return valid_permutations_for_row_grog_real(row, index, group_num, group_index)
    cache_key = (HashableList(get_encoding(row)),index, group_num, group_index)
    if cache_key in cache:
        # result = valid_permutations_for_row_grog_real(row, index, group_num, group_index)
        cached = cache[cache_key]
        # if result != cached:
        #     print("cache hit", row, cache_key, cache[cache_key])
        #     print("Cached from", debug_cache[cache_key])
        #     print("New result", result)
        return cache[cache_key]
    else:
        result = valid_permutations_for_row_grog_real(row, index, group_num, group_index)
        cache[cache_key] = result
        debug_cache[cache_key] = row
        return result

def valid_permutations_for_row_grog_real(row: Row, index: int, group_num: int, group_index: int) -> int:
    if index >= len(row.springs) or num_questions(row) == 0:
        if is_valid(row):
            return 1
        else:
            return 0
    if not grog_could_be_valid(row):
        return 0
    c = row.springs[index]
    if c == ".":
        if group_index > 0:
            if row.encoding[group_num] < group_index:
                return 0
            return valid_permutations_for_row_grog(row, index + 1, group_num+1, 0)
        else:
            return valid_permutations_for_row_grog(row, index + 1, group_num, group_index)
    if c == "#":
        if group_num >= len(row.encoding):
            return 0
        if group_index >= row.encoding[group_num]:
            return 0
        return valid_permutations_for_row_grog(row, index + 1, group_num, group_index+1)
    if c == "?":
        damaged_count = 0
        valid_count = 0
        if group_index == 0 or group_index < row.encoding[group_num]:
            damaged = Row(row.springs[:index]+"#"+row.springs[index+1:], row.encoding)
            damaged_count = valid_permutations_for_row_grog(damaged, index, group_num, group_index)
        if group_index == 0 or group_index >= row.encoding[group_num]:
            working = Row(row.springs[:index]+"."+row.springs[index+1:], row.encoding)
            valid_count = valid_permutations_for_row_grog(working, index, group_num, group_index)
        return damaged_count + valid_count
    print(c, index, row)

@dataclass
class HashableList:
    l: list
    def __hash__(self):
        return hash(tuple(self.l))

def solve(s: str) -> int:
    rows = [parse(r) for r in s.split("\n")]
    sum = 0
    total = len(rows)
    progress = 0
    for row in rows:
        # print(row)
        progress += 1
        # print(f"{progress}/{total}")
        # valid_rows = valid_permutations_for_row_try3(row)
        # valid_row_set = valid_permutations_for_row_try3_check(row)
        valid_rows = valid_permutations_for_row_grog(row, 0, 0, 0)
        cache.clear()
        sum += valid_rows
    return sum


print(solve(example))
print(solve(input)) # correct is 7361

badexample = """??#??#???##???????? 4,1,2,3,3"""

# 6234 is wrong, too low

def solve2(s: str) -> int:
    rows = [parse(r).mult5() for r in s.split("\n")]
    sum = 0
    total = len(rows)
    progress = 0
    for row in rows:
        # print(row)
        progress += 1
        print(f"{progress}/{total}")
        valid_rows = valid_permutations_for_row_grog(row,0, 0, 0)
        cache.clear()
        sum += valid_rows
    return sum

print(solve2(example))
# print(solve2(input))

# 23432027 is too low
# 83317216247365
