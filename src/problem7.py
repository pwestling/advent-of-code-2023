import math
import time
from dataclasses import dataclass
from typing import Optional

from util.resources import resource
from parsec import *

input = resource("problem7.txt")
example = """32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483"""

def ord(c: str) -> int:
    if c == "J":
        return 0
    if c in "TJQKA":
        return 10 + "TJQKA".index(c)
    else:
        return int(c)

def hand_sub_ord(s: str) -> list[int]:
    return [ord(c) for c in s]

def occurs_times(c: str, s: str) -> int:
    return len([x for x in s if x == c])

def hand_to_type_ord(s: str) -> int:
    occurences = [occurs_times(c, s) for c in set(s)]
    occurences.sort()
    occurences.reverse()
    if occurences == [5]: # five of a kind
        return 7
    elif occurences == [4,1]:  # four of a kind
        return 6
    elif occurences == [3,2]: # full house
        return 5
    elif occurences[0] == 3:
        return 4
    elif occurences == [2,2,1]: # two pair
        return 3
    elif occurences[0] == 2: # one pair
        return 2
    else:
        return 1

def solve(s: str) -> int:
    lines = s.split("\n")
    hands: list[tuple(str, int)] = []
    for line in lines:
        if line.strip():
            hand, bid = line.split(" ")
            hands.append((hand, int(bid)))
    hands.sort(key=lambda x: (hand_to_type_ord(x[0]), hand_sub_ord(x[0])))
    sum = 0
    for i in range(len(hands)):
        sum += (i+1) * hands[i][1]
    return sum

print(solve(example))
print(solve(input))


def hand_to_type_ord2(s: str) -> int:
    best = hand_to_type_ord(s)
    for i, c in enumerate(s):
        if c == "J":
            for k in set(s):
                if k != "J":
                    new_s = s[:i] + k + s[i+1:]
                    best = max(best, hand_to_type_ord2(new_s))
    return best

def solve2(s: str) -> int:
    lines = s.split("\n")
    hands: list[tuple(str, int)] = []
    for line in lines:
        if line.strip():
            hand, bid = line.split(" ")
            hands.append((hand, int(bid)))
    hands.sort(key=lambda x: (hand_to_type_ord2(x[0]), hand_sub_ord(x[0])))
    sum = 0
    for i in range(len(hands)):
        sum += (i+1) * hands[i][1]
    return sum

print(solve2(example))
print(hand_to_type_ord2("T55J5"))
print(hand_sub_ord("T55J5"))
print(hand_sub_ord("KTJJT"))

print(len(input.split("\n")))
print(solve2(input))