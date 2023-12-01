
from util.resources import resource
from parsec import *

example = """1abc2
pqr3stu8vwx
a1b2c3d4e5f
treb7uchet"""

input = resource("problem1.txt")


def find_first_digit(s: str) -> int:
    """Find the first digit in a string."""
    for i, c in enumerate(s):
        if c.isdigit():
            return int(c)
    return None

def find_last_digit(s: str) -> int:
    last = None
    for i, c in enumerate(s):
        if c.isdigit():
            last = int(c)
    return last


def solve(s):
    # get the lines of s
    lines_of_s = s.split("\n")
    sum = 0
    for l in lines_of_s:
        first = find_first_digit(l)
        last = find_last_digit(l)
        sum += first*10+last
    return sum

print(solve(example))
print(solve(input))


# part 2

digit_word_map = {
   "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven":7,
    "eight": 8,
    "nine": 9,
}

def find_first_digit2(s: str) -> int:
    """Find the first digit in a string."""
    for i, c in enumerate(s):
        if c.isdigit():
            return int(c)
        for k in digit_word_map.keys():
            if s[i:].startswith(k):
                return digit_word_map[k]

    return None

def find_last_digit2(s: str) -> int:
    """Find the first digit in a string."""
    last = None
    for i, c in enumerate(s):
        if c.isdigit():
            last = int(c)
        for k in digit_word_map.keys():
            if s[i:].startswith(k):
                last = digit_word_map[k]

    return last

example2 = """two1nine
eightwothree
abcone2threexyz
xtwone3four
4nineeightseven2
zoneight234
7pqrstsixteen"""

def solve2(s):
    # get the lines of s
    lines_of_s = s.split("\n")
    sum = 0
    for l in lines_of_s:
        first = find_first_digit2(l)
        last = find_last_digit2(l)
        sum += first*10+last
    return sum

print(solve2(example2))
print(solve2(input))