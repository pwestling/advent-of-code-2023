from dataclasses import dataclass

from util.resources import resource
from parsec import *


example1 = """Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green"""

@dataclass
class DrawSet:
    blue: int
    red: int
    green: int

    def __add__(self, other):
        return DrawSet(self.blue + other.blue, self.red + other.red, self.green + other.green)

@dataclass
class Game:
    game_id: int
    draws: list[DrawSet]

    def is_possible_on(self, draw: DrawSet) -> bool:
        return all(
            draw.blue >= d.blue and draw.red >= d.red and draw.green >= d.green
            for d in self.draws
        )

@generate
def color_draw() -> DrawSet:
    number_str = yield many1(digit())
    yield spaces()
    color = yield regex("(blue)|(red)|(green)")
    result = DrawSet(0, 0, 0)
    num = int("".join(number_str))
    match color:
        case "blue":
            result.blue = num
        case "red":
            result.red = num
        case "green":
            result.green = num
    return result

@generate
def game_draws() -> DrawSet:
    draws = yield sepBy(color_draw, string(", "))
    out = DrawSet(0, 0, 0)
    for d in draws:
        out += d
    return out


@generate
def parse_game() -> Game:
    yield string("Game ")
    game_id = yield many1(digit())
    yield string(": ")
    game_contents = yield sepBy(game_draws, string("; "))
    result = Game(int("".join(game_id)), game_contents)
    return result
@generate
def parse_all() -> list[Game]:
    result = yield sepBy(parse_game, string("\n"))
    return result

print(parse(color_draw, "3 blue"))
print(parse(parse_all, example1))

example_games = parse(parse_all, example1)

def solve(games: list[Game], draws_set: DrawSet) -> int:
    return sum([g.game_id for g in games if g.is_possible_on(draws_set)])

print(solve(example_games, DrawSet(12, 13, 14)))
input = resource("problem2.txt")
print(solve(parse(parse_all, input), DrawSet(red=12, green=13, blue=14)))

# part 2

def min_size(games: Game) -> DrawSet:
    min_green = max(d.green for d in games.draws)
    min_blue = max(d.blue for d in games.draws)
    min_red = max(d.red for d in games.draws)
    x = DrawSet(min_blue, min_red, min_green)
    return x

def power(set: DrawSet) -> int:
    return set.blue * set.red * set.green

def solve2(games: list[Game]) -> int:
    return sum(power(min_size(g)) for g in games)

print(solve2(example_games))
print(solve2(parse(parse_all, input)))