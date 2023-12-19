import functools
import math
import time
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

input = resource("problem19.txt")

example = """px{a<2006:qkq,m>2090:A,rfg}
pv{a>1716:R,A}
lnx{m>1548:A,A}
rfg{s<537:gd,x>2440:R,A}
qs{s>3448:A,lnx}
qkq{x<1416:A,crn}
crn{x>2662:A,R}
in{s<1351:px,qqz}
qqz{s>2770:qs,m<1801:hdj,R}
gd{a>3333:R,R}
hdj{m>838:A,pv}

{x=787,m=2655,a=1222,s=2876}
{x=1679,m=44,a=2067,s=496}
{x=2036,m=264,a=79,s=2244}
{x=2461,m=1339,a=466,s=291}
{x=2127,m=1623,a=2188,s=1013}"""

class Mode(Enum):
    GT = 1
    LT = 2

class Attr(Enum):
    X = 1
    M = 2
    A = 3
    S = 4
@dataclass
class Rule:
    target: Attr
    mode: Mode
    num: int
    dest: str

    def invert(self) -> "Rule":
        if self.mode == Mode.GT:
            return Rule(self.target, Mode.LT, self.num+1, "N")
        elif self.mode == Mode.LT:
            return Rule(self.target, Mode.GT, self.num-1, "N")
        else:
            raise Exception("Invalid identifier")

@dataclass
class Ruleset:
    name: str
    rules: list[Rule]
    dest: str

@generate
def parse_identifier() -> str:
    name = yield many1(letter())
    return "".join(name)

@generate
def parse_rule() -> Rule:
    rest = yield one_of("xmas")
    if rest == "x":
        attr = Attr.X
    elif rest == "m":
        attr = Attr.M
    elif rest == "a":
        attr = Attr.A
    elif rest == "s":
        attr = Attr.S
    else:
        raise Exception("Invalid identifier")
    op = yield one_of("<>")
    if op == "<":
        mode = Mode.LT
    elif op == ">":
        mode = Mode.GT
    else:
        raise Exception("Invalid identifier")
    num = yield many1(digit())
    yield string(":")
    dest = yield parse_identifier
    return Rule(attr, mode, int("".join(num)), "".join(dest))
@generate
def parse_ruleset() -> Ruleset:
    name = yield parse_identifier
    yield string("{")
    rules = yield sepBy1(parse_rule, string(","))
    yield string(",")
    dest = yield parse_identifier
    yield string("}")
    return Ruleset(name, rules, dest)

@dataclass
class Item:
    x : int
    m : int
    a : int
    s : int

@generate
def parse_item() -> Item:
    yield string("{")
    yield string("x=")
    x = yield many1(digit())
    yield string(",")
    yield string("m=")
    m = yield many1(digit())
    yield string(",")
    yield string("a=")
    a = yield many1(digit())
    yield string(",")
    yield string("s=")
    s = yield many1(digit())
    yield string("}")
    return Item(int("".join(x)), int("".join(m)), int("".join(a)), int("".join(s)))


def parse_input(s: str) -> tuple[dict[str, Ruleset], list[Item]]:
    parts = s.split("\n\n")
    ruleset = [parse(parse_ruleset,l) for l in parts[0].split("\n")]
    rulemap = {}
    for r in ruleset:
        rulemap[r.name] = r
    items = []
    for line in parts[1].split("\n"):
        items.append(parse(parse_item, line))
    return rulemap, items

print(parse_input(example))

def execute_rule(rule: Rule, item: Item) -> Optional[str]:
    if rule.target == Attr.X:
        val = item.x
    elif rule.target == Attr.M:
        val = item.m
    elif rule.target == Attr.A:
        val = item.a
    elif rule.target == Attr.S:
        val = item.s
    else:
        raise Exception("Invalid identifier")
    if rule.mode == Mode.GT:
        if val > rule.num:
            return rule.dest
    elif rule.mode == Mode.LT:
        if val < rule.num:
            return rule.dest
    else:
        raise Exception("Invalid identifier")
    return None

def execute_ruleset(ruleset: Ruleset, item: Item) -> str:
    for rule in ruleset.rules:
        result = execute_rule(rule, item)
        if result is not None:
            return result
    return ruleset.dest

def execute(rules: dict[str, Ruleset], item: Item) -> int:
    ruleset = rules["in"]
    while True:
        next_ruleset = execute_ruleset(ruleset, item)
        if next_ruleset == "R":
            return 0
        elif next_ruleset == "A":
            return item.x + item.m + item.a + item.s
        else:
            ruleset = rules[next_ruleset]


def solve1(rules: dict[str, Ruleset], items: list[Item]) -> int:
    return sum([execute(rules, item) for item in items])

print(solve1(*parse_input(example)))
print(solve1(*parse_input(input)))


@dataclass
class Range:
    min: int
    max: int

    def __len__(self):
        return self.max - self.min + 1
@dataclass
class ItemVals:
    x : Range
    m : Range
    a : Range
    s : Range

@dataclass
class RuleLoc:
    ruleset: str
    rule_index: int


class RulesetListSearchSpace(SearchSpace[RuleLoc, Rule]):

    def __init__(self, rules: dict[str, Ruleset]):
        self.rules = rules
    def actions(self, state: RuleLoc) -> list[Rule]:
        if state.ruleset == "A" or state.ruleset == "R":
            return []
        if state.rule_index >= len(self.rules[state.ruleset].rules):
            return [Rule(Attr.X, Mode.GT, -1, self.rules[state.ruleset].dest)]
        rule = self.rules[state.ruleset].rules[state.rule_index]
        return [rule, rule.invert()]

    def result(self, state: RuleLoc, action: Rule) -> RuleLoc:
        if action.dest == "N":
            return RuleLoc(state.ruleset, state.rule_index + 1)
        else:
            return RuleLoc(action.dest, 0)

    def cost(self, state: RuleLoc, action: Rule) -> float:
        return 0

    def states(self) -> list[State]:
        pass

def solve2(rules: dict[str, Ruleset], _) -> int:
    space = RulesetListSearchSpace(rules)
    paths = find_all_paths(space, RuleLoc("in", 0), RuleLoc("A",0))

    good_val_sets = []
    for p in paths:
        itemvals = ItemVals(Range(1,4000),Range(1,4000),Range(1,4000),Range(1,4000))
        for rule in p:
            if rule.target == Attr.X:
                valset = itemvals.x
            elif rule.target == Attr.M:
                valset = itemvals.m
            elif rule.target == Attr.A:
                valset = itemvals.a
            elif rule.target == Attr.S:
                valset = itemvals.s

            if rule.mode == Mode.GT:
                valset = Range(max(valset.min, rule.num + 1), valset.max)
            elif rule.mode == Mode.LT:
                valset = Range(valset.min, min(valset.max, rule.num - 1))

            if rule.target == Attr.X:
                itemvals.x = valset
            elif rule.target == Attr.M:
                itemvals.m = valset
            elif rule.target == Attr.A:
                itemvals.a = valset
            elif rule.target == Attr.S:
                itemvals.s = valset

        good_val_sets.append(itemvals)

    sum = 0
    for good_vals in good_val_sets:
        sum += len(good_vals.x) * len(good_vals.m) * len(good_vals.a) * len(good_vals.s)
    return sum



e = solve2(*parse_input(example))
print(e)
if e != 167409079868000:
    print("Bad example")

print(solve2(*parse_input(input)))
