import math
from dataclasses import dataclass
from typing import Optional

from util.resources import resource
from parsec import *

input = resource("problem5.txt")
example = """seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4"""

@dataclass
class Range:
    start_one: int
    start_two: int
    length: int

    def map(self, i: int) -> Optional[int]:
        if self.start_one <= i <= self.start_one + self.length:
            x = (self.start_two - self.start_one) + i
            return x
        else:
            return None


@generate
def parse_range() -> Range:
    start_two = yield many1(digit())
    yield spaces()
    start_one = yield many1(digit())
    yield spaces()
    length = yield many1(digit())
    return Range(int("".join(start_one)), int("".join(start_two)), int("".join(length)))

@dataclass
class Map:
    ranges: list[Range]

    def map(self, i: int) -> int:
        for r in self.ranges:
            result = r.map(i)
            if result is not None:
                return result
        return i

@generate
def parse_map() -> Map:
    yield many1(none_of("\n"))
    yield spaces()
    ranges = yield sepBy(parse_range, string("\n"))
    return Map(ranges)

@generate
def parse_seeds() -> list[int]:
    yield string("seeds: ")
    seeds = yield sepBy(many1(digit()), string(" "))
    return [int("".join(s)) for s in seeds]
@dataclass
class Problem:
    seeds : list[int]
    seed_to_soil : Map
    soil_to_fertilizer : Map
    fertilizer_to_water : Map
    water_to_light : Map
    light_to_temperature : Map
    temperature_to_humidity : Map
    humidity_to_location : Map

    def map(self, seed: int) -> int:
        soil = self.seed_to_soil.map(seed)
        fertilizer = self.soil_to_fertilizer.map(soil)
        water = self.fertilizer_to_water.map(fertilizer)
        light = self.water_to_light.map(water)
        temperature = self.light_to_temperature.map(light)
        humidity = self.temperature_to_humidity.map(temperature)
        location = self.humidity_to_location.map(humidity)
        return location


@generate
def parse_problem() -> Problem:
    seeds = yield parse_seeds
    yield string("\n\n")
    seed_to_soil = yield parse_map
    yield string("\n\n")
    soil_to_fertilizer = yield parse_map
    yield string("\n\n")
    fertilizer_to_water = yield parse_map
    yield string("\n\n")
    water_to_light = yield parse_map
    yield string("\n\n")
    light_to_temperature = yield parse_map
    yield string("\n\n")
    temperature_to_humidity = yield parse_map
    yield string("\n\n")
    humidity_to_location = yield parse_map
    return Problem(seeds, seed_to_soil, soil_to_fertilizer, fertilizer_to_water, water_to_light, light_to_temperature, temperature_to_humidity, humidity_to_location)

print(parse(parse_problem, example))

def solve(input: str) -> int:
    problem = parse(parse_problem, input)
    results = []
    for seed in problem.seeds:
        results.append(problem.map(seed))
    return min(results)

print(solve(example))
print(solve(input))

