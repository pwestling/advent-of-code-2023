from dataclasses import dataclass

from util.resources import resource
from parsec import *

input = resource("problem3.txt")
example = """467..114..
...*......
..35..633.
......#...
617*......
.....+.58.
..592.....
......755.
...$.*....
.664.598.."""

def as_matrix(s: str):
    return [[c for c in line] for line in s.split("\n")]


def is_adjacent_to_symbol(a: tuple[int, int], matrix: list[list[str]]) -> bool:
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0:
                continue
            if 0 <= a[0] + i < len(matrix) and 0 <= a[1] + j < len(matrix[0]):
                d = matrix[a[0] + i][a[1] + j]
                # Check that d is not alphanum
                if not d.isalpha() and not d.isdigit() and not d == ".":
                    return True


def get_adjacent_number(a: tuple[int, int], matrix: list[list[str]]) -> tuple[int, int]:
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0:
                continue
            if 0 <= a[0] + i < len(matrix) and 0 <= a[1] + j < len(matrix[0]):
                d = matrix[a[0] + i][a[1] + j]
                # Check that d is not alphanum
                if d.isdigit():
                    if is_adjacent_to_symbol((a[0] + i, a[1] + j), matrix):
                        return (a[0] + i, a[1] + j)


def find_full_num(a: tuple[int, int], matrix: list[list[str]]) -> tuple[int, int, int]:
    i = -1
    prefix = ""
    while a[1] + i >= 0 and matrix[a[0]][a[1] + i].isdigit():
        prefix = matrix[a[0]][a[1] + i] + prefix
        i -= 1
    j = 1
    suffix = ""
    while a[1] + j < len(matrix[0]) and matrix[a[0]][a[1] + j].isdigit():
        suffix += matrix[a[0]][a[1] + j]
        j += 1
    return int(prefix + matrix[a[0]][a[1]] + suffix), len(suffix), len(prefix)



def solve(matrix: list[list[str]]):
    length = len(matrix)
    width = len(matrix[0])
    sum = 0
    for i in range(length):
        for j in range(width):
            if matrix[i][j].isdigit():
                if is_adjacent_to_symbol((i, j), matrix):
                    num, num_len, _ = find_full_num((i, j), matrix)
                    sum += num
                    for k in range(num_len + 1):
                        matrix[i][j + k] = "."

    return sum

print(solve(as_matrix(example)))
print(solve(as_matrix(input)))

#part 2

def solve2(matrix: list[list[str]]):
    length = len(matrix)
    width = len(matrix[0])
    sum = 0
    for i in range(length):
        for j in range(width):
            if matrix[i][j] == "*":
                # make a copy of the matrix
                matrix_copy = [row[:] for row in matrix]
                num1_loc = get_adjacent_number((i, j), matrix)
                if not num1_loc:
                    continue
                num1, num_len_suff, num_len_pref = find_full_num(num1_loc, matrix)
                # wipe out num1 from the matrix
                for k in range(num_len_suff + num_len_pref + 1):
                    matrix[num1_loc[0]][num1_loc[1] + k - num_len_pref] = "."

                num2_loc = get_adjacent_number((i, j), matrix)
                if not num2_loc:
                    continue
                num2, num_len_suff, num_len_pref = find_full_num(num2_loc, matrix)
                # wipe out num2 from the matrix
                for k in range(num_len_suff + num_len_pref + 1):
                    matrix[num2_loc[0]][num2_loc[1] + k - num_len_pref] = "."

                num3_loc = get_adjacent_number((i, j), matrix)
                if num3_loc:
                    matrix = matrix_copy
                    continue

                gear_ratio = num2 * num1
                sum += gear_ratio

    return sum

example2 = """467..114..
...*......
..35..633.
......#...
617*......
.....+.58.
..592.....
......755.
...$.*....
.664.598.."""

print(solve2(as_matrix(example2)))
print(solve2(as_matrix(input)))