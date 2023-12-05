import math
import time
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
    start: int
    length: int

@dataclass
class RangeMap:
    start_one: int
    start_two: int
    length: int

    def map(self, i: int) -> Optional[int]:
        if self.start_one <= i <= self.start_one + self.length:
            x = (self.start_two - self.start_one) + i
            return x
        else:
            return None

    def map_range(self, r: Range) -> list[Range]:
        results = []
        input = Range(r.start, r.length)
        # handle the portion of the range before the map, if any
        if r.start < self.start_one:
            unmapped_length = min(input.length, self.start_one - input.start)
            results.append(Range(input.start, unmapped_length))
            input.length -= unmapped_length
            input.start += unmapped_length
        else:
            results.append(None)
        # handle the portion of the range in the map, if any
        if self.start_one <= input.start <= self.start_one + self.length:
            unmapped_length = min(input.length, self.length)
            results.append(Range(self.map(input.start), unmapped_length))
            input.length -= unmapped_length
            input.start += unmapped_length
        else:
            results.append(None)
        # handle the portion of the range after the map, if any
        if input.length > 0:
            results.append(input)
        else:
            results.append(None)
        return results




@generate
def parse_range() -> RangeMap:
    start_two = yield many1(digit())
    yield spaces()
    start_one = yield many1(digit())
    yield spaces()
    length = yield many1(digit())
    return RangeMap(int("".join(start_one)), int("".join(start_two)), int("".join(length)))

@dataclass
class Map:
    ranges: list[RangeMap]

    def map(self, i: int) -> int:
        for r in self.ranges:
            result = r.map(i)
            if result is not None:
                return result
        return i

    def map_range(self, r: Range) -> list[Range]:
        return self.map_range_recur(r, self.ranges)


    def map_range_recur(self, r: Range, range_maps: list[RangeMap]) -> list[Range]:
        results = []
        if not r:
            return []
        if len(range_maps) == 0:
            return [r]
        front, middle, back = range_maps[0].map_range(r)
        if middle is not None and middle.length > 0:
            results.append(middle)
        if front is not None and front.length > 0:
            results += self.map_range_recur(front, range_maps[1:])
        if back is not None and back.length > 0:
            results += self.map_range_recur(back, range_maps[1:])
        return results


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

def flatten_ranges(ranges: list[list[Range]]) -> list[Range]:
    results = []
    for r in ranges:
        results += r
    return results

def solve2(input: str) -> int:
    problem = parse(parse_problem, input)
    seed_ranges: list[Range] = []
    results = []
    for i in range(0, len(problem.seeds), 2):
        seed_start = problem.seeds[i]
        seed_length = problem.seeds[i+1]
        seed_ranges.append(Range(seed_start, seed_length))
    for seed_range in seed_ranges:
        ranges = problem.seed_to_soil.map_range(seed_range)
        ranges = flatten_ranges([problem.soil_to_fertilizer.map_range(r) for r in ranges])
        ranges = flatten_ranges([problem.fertilizer_to_water.map_range(r) for r in ranges])
        ranges = flatten_ranges([problem.water_to_light.map_range(r) for r in ranges])
        ranges = flatten_ranges([problem.light_to_temperature.map_range(r) for r in ranges])
        ranges = flatten_ranges([problem.temperature_to_humidity.map_range(r) for r in ranges])
        ranges = flatten_ranges([problem.humidity_to_location.map_range(r) for r in ranges])
        results.append(min([r.start for r in ranges]))

    return min(results)

print(solve2(example))
start = time.time_ns()
print(solve2(input))
end = time.time_ns()
print("Took " +  str(end-start) + " nanosecond")
