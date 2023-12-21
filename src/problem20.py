import functools
import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from util.search import *

from src.util.search import AdjacentMatrixSearchSpace
from util.resources import resource
from util.timer import timed
# from parsec import *
from util.grid import *
import itertools
from tqdm import tqdm
from scipy.sparse import dok_matrix

input = resource("problem20.txt")

example = """broadcaster -> a, b, c
%a -> b
%b -> c
%c -> inv
&inv -> a"""

interesting = """broadcaster -> a
%a -> inv, con
&inv -> b
%b -> con
&con -> output"""


smallerexample = """broadcaster -> one
%one -> two
%two -> four,  inv
&inv -> fake, conjone 
%four -> eight,  conjone
%eight -> sixteen
%sixteen -> thirtytwo, four
&conjone -> rx"""


class PulseStrength(Enum):
    LOW = 1
    HIGH = 2

class ComponentType(Enum):
    BROADACST = "BROADCAST"
    CONJUNCTION = "CONJUNCTION"
    FLIPFLOP = "FLIPFLOP"
    UNTYPED = "UNTYPED"

    def __str__(self):
        return self.name

@dataclass
class Component:
    name: str
    type: ComponentType
    dests: list[str]
    memory: dict[str, PulseStrength]
    onoff: bool
    state_sequence: "list[tuple[int, Optional[PulseStrength]]]"
    flip_flop_period: int
    parents: "list[str]"
    children: "list[str]" = field(default_factory=list)
    sent_this_run: list[PulseStrength] = field(default_factory=list)
    last_sent: Optional[PulseStrength] = None
    is_inverter: bool = False


    # def capture_state(self):
    #     state = (self.memory.copy(), self.onoff)
    #     if self.time_to_cycle == -1 and all(p.time_to_cycle != -1 for p in self.parents):
    #         if state in self.state_sequence:
    #
    #     self.state_sequence.append(state)


def parse_component(s :str) -> Component:
    parts = s.split("->")
    name = parts[0].strip()
    dests = [s.strip() for s in parts[1].split(",")]
    if s.startswith("%"):
        return Component(name[1:], ComponentType.FLIPFLOP, dests, {}, False, [], -1, [])
    elif s.startswith("&"):
        return Component(name[1:], ComponentType.CONJUNCTION, dests, {}, False, [], -1, [])
    elif name == "broadcaster":
        return Component(name, ComponentType.BROADACST, dests, {}, False, [], -1, [])
    else:
        raise Exception("Invalid component")


def parse(s: str) -> dict[str, Component]:
    compmap = {c.name: c for c in map(parse_component, s.split("\n"))}
    for c in list(compmap.values()):
        for d in c.dests:
            if d not in compmap:
                compmap[d] = Component(d, ComponentType.UNTYPED, [], {}, False, [], -1, [])

    for c in compmap.values():
        for c2 in compmap.values():
            if c.name in c2.dests:
                c.parents.append(c2.name)
                c2.children.append(c.name)
            if c.type == ComponentType.CONJUNCTION and len(c.parents) == 1:
                c.is_invereter = True

    for c in list(compmap.values()):
        for d in c.dests:
            if d in compmap and compmap[d].type == ComponentType.CONJUNCTION:
                compmap[d].memory[c.name] = PulseStrength.LOW
    return compmap



@dataclass
class PulseResults:
    high: int
    low: int
    rx_triggered: bool = False

    def __add__(self, other):
        return PulseResults(self.high + other.high, self.low + other.low, other.rx_triggered or self.rx_triggered)

def do_append(iter: int, source: Component, queue: list[tuple[Component, PulseStrength, str]], components: dict[str, Component], dest: str, strength: PulseStrength):
    source.sent_this_run.append(strength)
    source.last_sent = strength
    # source.state_sequence.append((iter, strength))
    if dest in components:
        c = components[dest]
        queue.append((c, strength, source.name))
    else:
        queue.append((None, strength, source.name))
        # print(f"{source.name} {strength} -> {c.name}")

def run(components: dict[str, Component], iter: int) -> PulseResults:
    results = PulseResults(0,0)
    for c in components.values():
        c.sent_this_run = []

    queue = [(components["broadcaster"], PulseStrength.LOW, "button")]
    while queue:
        c, strength, source = queue.pop(0)
        if strength == PulseStrength.HIGH:
            results.high += 1
        else:
            results.low += 1
        if c is None:
            continue
        if c.type == ComponentType.BROADACST:
            for d in c.dests:
                do_append(iter, c, queue, components, d, strength)
        elif c.type == ComponentType.CONJUNCTION:
            c.memory[source] = strength
            if all(v == PulseStrength.HIGH for v in c.memory.values()):
                for d in c.dests:
                    do_append(iter, c, queue, components, d, PulseStrength.LOW)
            else:
                for d in c.dests:
                    do_append(iter, c, queue, components, d, PulseStrength.HIGH)
        elif c.type == ComponentType.FLIPFLOP:
            if strength == PulseStrength.LOW:
                if c.onoff == True:
                    c.onoff = False
                    for d in c.dests:
                        do_append(iter, c, queue, components, d, PulseStrength.LOW)
                else:
                    c.onoff = True
                    for d in c.dests:
                        do_append(iter, c, queue, components, d, PulseStrength.HIGH)

    return results

def do_append2(source: Component, queue: list[tuple[Component, PulseStrength, str]], components: dict[str, Component], dest: str, strength: PulseStrength):
    if dest in components:
        c = components[dest]
        queue.append((c, strength, source.name))
    else:
        queue.append((None, strength, source.name))
        # print(f"{source.name} {strength} -> {c.name}")

def lcm(nums: list[int]) -> int:
    result = 1
    for n in nums:
        result = result * n // math.gcd(result, n)
    return result


def has_rx_child(c: Component, components: dict[str, Component], visited: set[str]) -> bool:
    if c.name in visited:
        return False
    visited.add(c.name)
    if c.name == "rx":
        return True
    else:
        return any(has_rx_child(components[p], components, visited) for p in c.children)

def prune(components: dict[str, Component]):
    for comp in list(components.values()):
        if not has_rx_child(comp, components, set()):
            print("Removing", comp.name)
            for other in components.values():
                if comp.name in other.parents:
                    other.parents.remove(comp.name)
                if comp.name in other.children:
                    other.children.remove(comp.name)
            del components[comp.name]

def run_multi(components: dict[str, Component]) -> int:

    prune(components)

    for c in components.values():
        for d in c.dests:
            if d in components and components[d].type == ComponentType.CONJUNCTION:
                components[d].memory[c.name] = PulseStrength.LOW

    components["broadcaster"].flip_flop_period = 1

    for c in components.values():
        parents = [components[p] for p in c.parents]
        if c.type == ComponentType.FLIPFLOP:
            if c.flip_flop_period == -1 and any(p.flip_flop_period != -1 for p in parents):
                c.flip_flop_period = min([p.flip_flop_period for p in parents]) * 2
                print("Calced flipflop", c.name, "to", c.flip_flop_period)

    return components["rx"].flip_flop_period


def run1k(components: dict[str, Component]) -> int:
    result = PulseResults(0,0)
    for i in range(1000):
        result += run(components, (i+1))
    return result.high * result.low

def runN(components: dict[str, Component], n: int, target: str, exclude: set[str], include: set[str]) -> Optional[PulseStrength]:
    result = PulseResults(0,0)
    for i in tqdm(range(n)):
        result += run(components, (i+1))
        # for c in components.values():
        #     if c.name not in exclude:
        #         if c.sent_this_run == PulseStrength.LOW and c.type == ComponentType.CONJUNCTION:
        #             print(i+1, c.name, c.sent_this_run)
        #     if c.name in include:
        #         print(i + 1, c.name, c.sent_this_run)
    if n < 1000:
        for c in components.values():
            print(c.name, end=": ")
            for s in c.state_sequence:
               print(f"{s[0]} {s[1].name}", end=" ")
            print()
    else:
        t = components[target]
        for s in t.state_sequence:
            if s[1] == PulseStrength.LOW:
                print(s)

class ComponentSearchSpace(SearchSpace[str, str]):
    def __init__(self, components: dict[str, Component]):
        self.components = components

    def actions(self, state: str) -> list[str]:
        if state in self.components:
            return self.components[state].dests
        else:
            return []

    def result(self, state: str, action: str) -> str:
        return action

    def cost(self, state: str, action: str) -> float:
        return 1

# print(runN(parse(interesting), 5, "output", {}, {}))
# exit(0)


# print(parse(example))
# print(run(parse(example)))
# if run1k(parse(example)) != 32000000:
#     raise Exception("Wrong Example")
# if run1k(parse(input)) != 807069600:
#     raise Exception("Wrong Input")

# comps = parse(input)
# for c in comps.values():
#     if c.type == ComponentType.CONJUNCTION:
#         if len(c.parents) == 1:
#             print(c.name, "is an inverter")

# print(run_multi(parse(smallerexample)))

# print(run_multi(parse(input)))

e = parse(smallerexample)
# prune(e)
# print(e)

i = parse(input)
i_space = ComponentSearchSpace(i)
# print(topo_sort(i_space, "broadcaster"))
import graphviz

def as_DOT(components: dict[str, Component], topo_sort_result: list[list[str]]) -> str:
    result = "digraph G {\n"

    for tier in topo_sort_result:
        # result += f"{{rank=same; l1[style=invis, shape=point]; "
        for n in tier:
            c = components[n[0]]
            if c.last_sent == PulseStrength.LOW:
                color = "fillcolor=red, style=filled"
            elif c.last_sent == PulseStrength.HIGH:
                color = "fillcolor=green, style=filled"
            else:
                color = "color=black"
            if c.type == ComponentType.CONJUNCTION:
                result += f"{c.name} [shape=box {color}];\n"
            elif c.type == ComponentType.FLIPFLOP:
                result += f"{c.name} [shape=oval {color}];\n"
            elif c.type == ComponentType.BROADACST:
                result += f"{c.name} [shape=ellipse {color}];\n"
            else:
                result += f"{c.name} [shape=octagon {color}];\n"
        # result += "}\n"
        for n in tier:
            c = components[n[0]]
            for d in c.dests:
                result += f"{c.name} -> {d};\n"
    result += "}"
    return result

from PIL import Image
import os
import io

def render_dot_to_image(i, topo, filename: str) -> None:
    if not os.path.exists(filename):
        dot_string = as_DOT(i, topo)
        graph = graphviz.Source(dot_string)
        image_bytes = graph.pipe(format="png", )
        # make a PIL image
        image = Image.open(io.BytesIO(image_bytes))
        image = image.reduce(4).convert('RGB')
        # Reducing Quality
        quality_val = 50
        image.save(filename, 'JPEG', quality=quality_val)
        print("Rendered", filename)

# render_dot_to_image(as_DOT(i, topo_sort(i_space, "broadcaster")), "out")


import imageio
def create_animation(image_filenames: list[str], output_filename: str, duration: float = 1) -> None:
    """
    Create an animation from a list of image files.

    :param image_filenames: List of paths to image files.
    :param output_filename: Path to save the output GIF file.
    :param duration: Duration of each frame in the animation (in seconds).
    """
    # images = []
    # for filename in image_filenames:
    #     images.append(imageio.imread(filename))
    # imageio.mimsave(output_filename, images, fps=5)

    q = 50  # Quality
    img, *imgs = [Image.open(f) for f in image_filenames]
    img.save(fp=output_filename, format='GIF', append_images=imgs, quality=q,
             save_all=True, duration=len(images)*0.2, loop=0, optimize=True)




    # Usage example (assuming you have a list of image filenames)

i = parse(input)
# for k in tqdm(range(3880*3+3)):
#     run(i, k)
#     if PulseStrength.LOW in i["bp"].sent_this_run:
#         print(k)
# print(i["bp"])
# print(i["fh"])
#
# bits = ""
# mask = ""
# print(i["bp"].parents)
# for n in ["kn", "fh", "lm", "rk", "fs", "kx", "gn", "cf", "tz", "gp", "rp", "jj"]:
#     c = i[n]
#     if n in i["bp"].dests:
#         mask += "1"
#     else:
#         mask += "0"
#     if n in i["bp"].parents:
#         if c.last_sent == PulseStrength.HIGH:
#             bits += "1"
#         else:
#             bits += "0"
# altb = ""
# for n in i["bp"].parents:
#     if c.last_sent == PulseStrength.HIGH:
#         altb += "1"
#     else:
#         altb += "0"
# print(altb)
# print(any(i[n].sent_this_run == PulseStrength.HIGH for n in i["bp"].parents))
#
# bits = "".join(list(reversed(bits)))
# mask = "".join(list(reversed(mask)))
#
# inverted_mask = "".join(["1" if c == "0" else "0" for c in mask])
#
# print(bits)
# print(int(bits, 2))
# print(mask)
# print(int(mask, 2))
# print(inverted_mask)
# print(int(inverted_mask, 2))
# print(i["bp"])

def flatten(l: list[list[str]]) -> list[str]:
    return list(itertools.chain.from_iterable(l))

def get_inverted_mask(components: dict[str, Component], node: str, register: str) -> str:


    registers = [register]
    while True:
        reg = components[registers[-1]]
        flip_flop_dest = [d for d in reg.dests if components[d].type == ComponentType.FLIPFLOP]
        if flip_flop_dest:
            registers.append(flip_flop_dest[0])
        else:
            break



    topo = topo_sort(ComponentSearchSpace(components), "broadcaster")
    full_topo = [t[0] for t in flatten(topo)]
    def get_rank(n: str) -> int:
        return full_topo.index(n)

    target = components[node]
    unsorted_parents = components[node].parents
    flip_flop_children = [c for c in components[node].children if components[c].type == ComponentType.FLIPFLOP]

    deduped = set(unsorted_parents + flip_flop_children)
    parents = sorted(deduped, key=get_rank)
    parents = registers

    print(node, parents)

    bits = ""
    mask = ""
    for n in parents:
        parent = components[n]
        if n in target.dests:
            mask += "1"
        else:
            mask += "0"
        if n in parents:
            if parent.last_sent == PulseStrength.HIGH:
                bits += "1"
            else:
                bits += "0"
    mask = "".join(list(reversed(mask)))

    inverted_mask = "".join(["1" if c == "0" else "0" for c in mask])
    return inverted_mask

inverted_mask = get_inverted_mask(i, "bp", "kn")
print(inverted_mask)
a = int(inverted_mask, 2)+1
print(a)

inverted_mask = get_inverted_mask(i, "pm", "sj")
print(inverted_mask)
b = int(inverted_mask, 2)+1
print(b)

inverted_mask = get_inverted_mask(i, "xn", "tg")
print(inverted_mask)
c = int(inverted_mask, 2)+1
print(c)

inverted_mask = get_inverted_mask(i, "bd", "vn")
print(inverted_mask)
d = int(inverted_mask, 2)+1
print(d)

print(lcm([a, b, c, d]))

r = 3768
for k in tqdm(range(r*5)):
    run(i, k)
    count = 1
    if PulseStrength.LOW in i["xn"].sent_this_run:
        print(k+1, end=" ")
        if k+1 == (r+1)*count+(count-1):
            print(True)
        else:
            print(False)
        count += 1

print(i["xn"])

# print(runN(parse(input), 10, "bp", {"tx", "nd", "pc", "vd"}, {"nd", "pc", "vd", "tx", "bd"}))

# for x in [2048, 8, 256, 512, 1024, 32, 1]:
#     print(70368744177664 % (2*x))


# 803469022158770842444288414160202761797514970261000061716480 is too high

# 987608569080 is too low
# 221453937522197
if __name__ == '__main__':
    images = []
    topo = topo_sort(i_space, "broadcaster")
    i = parse(input)

    # thread image generation
    import concurrent.futures

    # with concurrent.futures.ThreadPoolExecutor(8) as p:
    for x in range(10001):
        run(i, x)
        filename = f"images/{x}.jpeg"
        render_dot_to_image(i, topo, filename)
        images.append(filename)
        if x % 10000 == 0:
            create_animation(images, f'graph_animation_{x}.gif')

