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
from tqdm import tqdm

input = resource("problem15.txt")
example = """rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7"""

def hashalgo(s: str) -> int:
    sum = 0
    for c in s:
        sum += ord(c)
        sum = sum * 17
        sum = sum % 256
    return sum

def solve(s: str) -> int:
    parts = s.split(",")
    sum = 0
    for p in parts:
        sum += hashalgo(p)
    return sum

print(solve(example))
print(solve(input))


def do_op(s: str, lensbox: dict[int, list[tuple[str, int]]]) -> None:
    if "=" in s:
        parts = s.split("=")
        label = parts[0]
        focal = int(parts[1])
        box = lensbox.get(hashalgo(label), [])
        for i, (l, _) in enumerate(box):
            if l == label:
                box[i] = (l, focal)
                return
        box.append((label, focal))
        lensbox[hashalgo(label)] = box
    if "-" in s:
        parts = s.split("-")
        label = parts[0]
        box = lensbox.get(hashalgo(label), [])
        index = -1
        for i, (l, _) in enumerate(box):
            if l == label:
                index = i
                break
        if index != -1:
            box.pop(index)
        lensbox[hashalgo(label)] = box


def solve2(s: str) -> int:
    parts = s.split(",")
    lensbox: dict[int, list[tuple[str, int]]] = {}
    for p in parts:
        do_op(p, lensbox)

    sum = 0
    for box_num, lenses in lensbox.items():
        for slot, lens in enumerate(lenses):
            sum += (box_num + 1) * (slot + 1) * lens[1]

    return sum

print(solve2(example))
print(solve2(input))



