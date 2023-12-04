import math
from dataclasses import dataclass

from util.resources import resource
from parsec import *

input = resource("problem4.txt")
example = """Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11"""

def solve(input: str):
    lines = input.split("\n")
    sum = 0
    for line in lines:
        if line.strip():
            data = line.split(": ")[1]
            parts = data.split(" | ")
            winning_numbers = set([int(p) for p in  parts[0].split(" ") if p.strip()])
            numbers_present = set([int(p) for p in  parts[1].split(" ") if p.strip()])
            num_found = 0
            for i in numbers_present:
                if i in winning_numbers:
                    num_found += 1
            if num_found > 0:
                sum += math.pow(2, num_found-1)
    return int(sum)

print(solve(example))
print(solve(input))

# part 2

def indices_won(line: str) -> tuple[int, set[int]]:
    if line.strip():
        splits = [s for s in line.split(": ") if s.strip()]
        data = splits[1]
        index = int([s for s in splits[0].split(" ") if s.strip()][1])

        parts = data.split(" | ")
        winning_numbers = set([int(p) for p in parts[0].split(" ") if p.strip()])
        numbers_present = set([int(p) for p in parts[1].split(" ") if p.strip()])
        num_found = 0
        for i in numbers_present:
            if i in winning_numbers:
                num_found += 1
        if num_found > 0:
            return index, set(range(index+1, index+num_found+1))
        else:
            return index, set()

print(indices_won("Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53"))

def solve_2(input: str) -> int:
    lines = input.split("\n")
    first_pass_lookup = {}
    for i in range(len(lines) - 1, -1, -1):
        index, indices = indices_won(lines[i])
        first_pass_lookup[index] = indices

    reverse_keys = list(first_pass_lookup.keys())
    reverse_keys.sort()
    reverse_keys.reverse()

    second_pass_lookup = {}
    for k in reverse_keys:
        wins = first_pass_lookup[k]
        result = 0
        for won_index in wins:
            result += second_pass_lookup[won_index]
        second_pass_lookup[k] = result + 1

    vals: list[int] = list(second_pass_lookup.values())
    #sum the vals
    return sum(vals)

print(solve_2(example))
print(solve_2(input))

