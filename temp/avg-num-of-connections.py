from itertools import combinations
from math import pi
from random import random


N = 100
# N = 2
GRID_SIDE = 10
CONNECTION_RANGE = 1


def simulate(n=N, grid_side=GRID_SIDE, connection_range=CONNECTION_RANGE):
    nodes = [
        (
            random() * grid_side,
            random() * grid_side,
        )
        for _ in range(n)
    ]
    num_connections = 0
    for i, j in combinations(nodes, 2):
        num_connections += (i[0] - j[0]) ** 2 + (
            i[1] - j[1]
        ) ** 2 <= connection_range**2

    return num_connections

simul_count = 1_000_0
tot = 0

for _ in range(simul_count):
    tot += simulate()

empirical = (tot/simul_count)

print(empirical)

expected = pi * (CONNECTION_RANGE * CONNECTION_RANGE) * N * (N-1) / (GRID_SIDE * GRID_SIDE * 2)

print(expected)

print(100 * abs(expected - empirical) / expected )
