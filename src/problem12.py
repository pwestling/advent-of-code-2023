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


@functools.cache
def could_be_valid(row: Row) -> bool:
    groups_max = get_encoding(row, "#")
    groups_min = get_encoding(row, ".")

    if max(groups_max) < max(row.encoding):
        return False
    pound_count = 0
    for c in row.springs:
        if c == "#":
            pound_count += 1
    if pound_count > sum(row.encoding):
        return False
    question_count = 0
    for c in row.springs:
        if c == "?":
            question_count += 1
    if pound_count + question_count < sum(row.encoding):
        return False
    if len(groups_max) > len(row.encoding):
        return False
    return True
#
#
# @functools.cache
# def valid_permutations_for_row(row: Row) -> set[Row]:
#     rows = set()
#     if not could_be_valid(row):
#         return rows
#
#     if len(row.encoding) == 1:
#         if spring_count(row.springs.replace("?", "#")) == row.encoding[0]:
#             rows.add(Row(row.springs.replace("?", "#"), row.encoding))
#             return rows
#
#     has_question = False
#     for i, c in enumerate(row.springs):
#         if c == "?":
#             rows = rows.union(
#                 valid_permutations_for_row(Row(row.springs[:i] + "#" + row.springs[i + 1:], row.encoding)))
#             rows = rows.union(
#                 valid_permutations_for_row(Row(row.springs[:i] + "." + row.springs[i + 1:], row.encoding)))
#             has_question = True
#     if not has_question:
#         if is_valid(row):
#             rows.add(row)
#     return rows

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



@functools.cache
def valid_permutations_for_row_v2(row: Row) -> set[Row]:
    rows = set()
    # if not could_be_valid(row):
    #     return rows

    run_length = row.encoding[0]
    part_length = len(row.springs)
    for i in range(part_length - run_length + 1):
        s = row.springs
        valid = True
        for j in range(run_length):
            c = s[i + j]
            if c == ".":
                valid = False
                break
            if c == "?":
                s = s[:i + j] + "#" + s[i + j + 1:]
        if valid:
            s = s.replace("?", ".")
            rows.add(Row(s, row.encoding))
    return rows


def spring_count(s: str) -> int:
    return len([c for c in s if c == "#"])

@functools.cache
def permutations_that_sum_to(target: int, progress: int, row: Row) -> list[list[int]]:
    if len(row.encoding) == 0:
        return []
    result = []
    if len(row.encoding) == 1:
        return [[target - progress]]
    for i in range(row.encoding[0], target):
        result.extend([[i] + x for x in permutations_that_sum_to(target, progress + i, Row(row.springs, row.encoding[1:]))])
    return result
@functools.cache
def permutations_that_sum_to_revert(target: int, progress: int, remaining_groups: int) -> list[list[int]]:
    if remaining_groups == 0:
        return []
    result = []
    if remaining_groups == 1:
        return [[target - progress]]
    for i in range(target):
        result.extend([x + [i] for x in permutations_that_sum_to_revert(target, progress + i, remaining_groups - 1)])
    return result

def dedupe(l: list[list[int]]) -> list[list[int]]:
    result = []
    for x in l:
        z = sorted(x)
        if z not in result:
            result.append(z)
    return result


def can_be_valid(row: Row, possibility: list[int]) -> bool:
    # print(row.encoding, possibility)
    for i, p in enumerate(possibility):
        if p < row.encoding[i]:
            return False
    return True


def can_be_valid_sub_rows(possibility: list[int], sub_rows: list[Row]) -> bool:
    for i, row in enumerate(sub_rows):
        if not could_be_valid(row):
            return False
    return True


def handle_possibility(possibility: list[int], row: Row) -> set[Row]:
    # split thw row into sub rows and use the earlier attempt
    # to find the permutations for each sub row
    sub_rows = []
    start = 0
    for i, size in enumerate(possibility):
        sub_rows.append(Row(row.springs[start:start + size], [row.encoding[i]]))
        if i < len(possibility) - 1:
            sub_rows.append(Row(row.springs[start + size:start+size+1], [0]))
        start += size+1

    sub_row_permutations = [valid_permutations_for_row_v2(sub_row) for sub_row in sub_rows]
    # add together all the permutations
    these_posssibilities = set()
    for permutation in itertools.product(*sub_row_permutations):
        r = Row("".join([x.springs for x in permutation]), row.encoding)
        if is_valid(r):
            these_posssibilities.add(r)
    return these_posssibilities

import re

@functools.cache
def valid_permutations_for_row_try2(row: Row) -> set[Row]:
    # replace all contiguous groups of . with a single .
    row.springs = re.sub(r"\.{2,}", ".", row.springs)
    # print(row)
    #
    # print(f"Computing group possibilities for {len(row.encoding)} groups")
    # group_possibilities = permutations_that_sum_to_revert(len(row.springs) - (len(row.encoding) - 1), 0, len(row.encoding))
    # group_possibilities = permutations_that_sum_to(len(row.springs) - (len(row.encoding) - 1), 0, row)

    # print(row.encoding)
    # print(len(row.encoding))
    # print(len(row.springs.split(".")))
    things = []
    for i, e in enumerate(row.encoding):
        max = len(row.springs) - sum(row.encoding) + e - len(row.encoding) + 1
        erange = list(range(e, max+1))
        things.append(list(erange))
    l = 1
    for thing in things:
        l *= len(thing)
    group_possibilities = [list(x) for x in itertools.product(*things) if sum(x) == len(row.springs) - (len(row.encoding) - 1)]
    # print(len(group_possibilities))

    all_possibilities = set()
    # print("Trying possibilities")
    for m, possibility in enumerate(group_possibilities):
        # if m % 10 == 0:
            # print(f"{m}/{len(group_possibilities)}")
        all_possibilities = all_possibilities.union(handle_possibility(possibility, row))

    return all_possibilities

@functools.cache
def valid_permutations_for_row_try2(row: Row) -> set[Row]:
    # replace all contiguous groups of . with a single .
    row.springs = re.sub(r"\.{2,}", ".", row.springs)
    # print(row)
    #
    # print(f"Computing group possibilities for {len(row.encoding)} groups")
    # group_possibilities = permutations_that_sum_to_revert(len(row.springs) - (len(row.encoding) - 1), 0, len(row.encoding))
    # group_possibilities = permutations_that_sum_to(len(row.springs) - (len(row.encoding) - 1), 0, row)

    # print(row.encoding)
    # print(len(row.encoding))
    # print(len(row.springs.split(".")))
    things = []
    for i, e in enumerate(row.encoding):
        max = len(row.springs) - sum(row.encoding) + e - len(row.encoding) + 1
        erange = list(range(e, max+1))
        things.append(list(erange))
    l = 1
    for thing in things:
        l *= len(thing)
    group_possibilities = [list(x) for x in itertools.product(*things) if sum(x) == len(row.springs) - (len(row.encoding) - 1)]
    # print(len(group_possibilities))

    all_possibilities = set()
    # print("Trying possibilities")
    for m, possibility in enumerate(group_possibilities):
        # if m % 10 == 0:
            # print(f"{m}/{len(group_possibilities)}")
        all_possibilities = all_possibilities.union(handle_possibility(possibility, row))

    return all_possibilities

@dataclass
class HashableList:
    l: list
    def __hash__(self):
        return hash(tuple(self.l))

def valid_permutations_for_row_try3(row: Row) -> int:
    # replace all contiguous groups of . with a single .
    row.springs = re.sub(r"\.{2,}", ".", row.springs)
    sections = [s for s in row.springs.split(".") if len(s) > 0]
    # print(row)
    # print(sections)

    return valid_permutations_for_row_try3_recur(HashableList(sections), HashableList(row.encoding), 1)

@functools.cache
def valid_permutations_for_row_try3_recur(sections: HashableList, remaining_encodings: HashableList, depth: int) -> int:
    # print(depth, sections, remaining_encodings, )
    if len(sections.l) == 0 and len(remaining_encodings.l) == 0:
        # print("Done", depth, sections, remaining_encodings)
        return 1
    if len(sections.l) == 0:
        return 0
    if len(remaining_encodings.l) == 0:
        return 0
    section = sections.l[0]
    total_perms = 0
    for num_assigned_groups in range(1, len(remaining_encodings.l)+1):
        section_row = Row(section, remaining_encodings.l[:num_assigned_groups])
        # print(depth, section_row, remaining_encodings.l[num_assigned_groups:])
        trailing = valid_permutations_for_row_try3_recur(HashableList(sections.l[1:]), HashableList(remaining_encodings.l[num_assigned_groups:]), depth+1)
        if trailing != 0:
            permutations = len(valid_permutations_for_row_try2(section_row))

            # print(depth, section_row, num_assigned_groups, permutations, trailing, remaining_encodings.l[num_assigned_groups:])
            total_perms += permutations * trailing
    return total_perms



def valid_permutations_for_row_try3_check(row: Row) -> set[Row]:
    # replace all contiguous groups of . with a single .
    row.springs = re.sub(r"\.{2,}", ".", row.springs)
    sections = [s for s in row.springs.split(".") if len(s) > 0]
    # print(row)
    # print(sections)

    return valid_permutations_for_row_try3_recur_check(HashableList(sections), HashableList(row.encoding), 1)

@functools.cache
def valid_permutations_for_row_try3_recur_check(sections: HashableList, remaining_encodings: HashableList, depth: int) -> set[Row]:
    # print(depth, sections, remaining_encodings, )
    if len(sections.l) == 1:
        return valid_permutations_for_row_try2(Row(sections.l[0], remaining_encodings.l))
    if len(sections.l) == 0:
        return set()
    if len(remaining_encodings.l) == 0:
        return set()
    section = sections.l[0]
    total_perms = set()
    for num_assigned_groups in range(1, len(remaining_encodings.l)+1):
        section_row = Row(section, remaining_encodings.l[:num_assigned_groups])
        # print(depth, section_row, remaining_encodings.l[num_assigned_groups:])
        trailing = valid_permutations_for_row_try3_recur_check(HashableList(sections.l[1:]), HashableList(remaining_encodings.l[num_assigned_groups:]), depth+1)
        if trailing is not None and len(trailing) > 0:
            permutations = valid_permutations_for_row_try2(section_row)
            for p, t in itertools.product(permutations, trailing):
                total_perms.add(Row(p.springs + t.springs, p.encoding + t.encoding))

            # print(depth, section_row, num_assigned_groups, permutations, trailing, remaining_encodings.l[num_assigned_groups:])
            # total_perms += permutations * trailing
    return total_perms

def valid_permutations_for_row_times_5(row: Row) -> set[Row]:
    permutations = valid_permutations_for_row_try2(row)

    start_spring_end_empty_base = 0
    start_empty_end_spring_base = 0
    both_spring_base = 0
    both_empty_base = 0
    print("permutes")

    def has_shifty_tail(orig: Row, r: Row) -> bool:
        ends_in_spring = r.springs[-1] == "#"
        end_group_size = orig.encoding[-1]

    for p in permutations:
        print(p)
        if p.springs[0] == "#" and p.springs[-1] == ".":
            start_spring_end_empty_base += 1
        if p.springs[0] == "." and p.springs[-1] == "#":
            start_empty_end_spring_base += 1
        if p.springs[0] == "#" and p.springs[-1] == "#":
            both_spring_base += 1
        if p.springs[0] == "." and p.springs[-1] == ".":
            both_empty_base += 1

    print(row, start_spring_end_empty_base, start_empty_end_spring_base, both_spring_base, both_empty_base)

    start_spring_end_empty_accum = start_spring_end_empty_base
    start_empty_end_spring_accum = start_empty_end_spring_base
    both_spring_accum = both_spring_base
    both_empty_accum = both_empty_base

    for i in range(5):
        start_spring_end_empty_new = (start_spring_end_empty_accum * start_spring_end_empty_base * 2) + (both_spring_accum * both_empty_base * 2) + (both_spring_accum * start_spring_end_empty_base)
        start_empty_end_spring_new = (start_empty_end_spring_accum * start_empty_end_spring_base * 2) + (both_empty_accum * both_spring_base * 2) + (both_empty_accum * start_empty_end_spring_base)
        both_spring_new = (both_spring_accum * both_spring_base) + (start_spring_end_empty_accum * start_empty_end_spring_base) + (both_spring_accum * start_empty_end_spring_base * 2)
        both_empty_new = (both_empty_accum * both_empty_base) + (start_empty_end_spring_accum * start_spring_end_empty_base) + (both_empty_accum * start_spring_end_empty_base * 2)


        start_empty_end_spring_accum = start_empty_end_spring_new
        start_spring_end_empty_accum = start_spring_end_empty_new
        both_spring_accum = both_spring_new
        both_empty_accum = both_empty_new
        print(row, start_spring_end_empty_accum, start_empty_end_spring_accum, both_spring_accum, both_empty_accum)

    print(start_spring_end_empty_accum + start_empty_end_spring_accum + both_spring_accum + both_empty_accum)
    return start_spring_end_empty_accum + start_empty_end_spring_accum + both_spring_accum + both_empty_accum




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
        check_valid_rows = valid_permutations_for_row_try2(row)
        cache.clear()
        if len(check_valid_rows) != valid_rows:
            print("ERROR")
            print(row)
            print(valid_rows)
            print(len(check_valid_rows))


        # print(valid_rows)
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
