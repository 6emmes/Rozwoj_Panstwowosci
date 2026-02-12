import heapq

import numpy as np

from utils.definitions import Grid, Point
from world import World

SQRT_2 = np.sqrt(2)
H = 3
A = 5
B = 4.6

heigit_eff = lambda x: H * (np.exp(x) - 1) + 1
river_eff = lambda x: A * np.exp(-B * x)


def _cost(world: World, x: int, y: int) -> float:
    if world.water[x][y] == 0:
        return float("inf")
    river = river_eff(world.heightmap[x][y]) if world.rivers[x][y] > 0 else 0
    return max(0.1, heigit_eff(world.heightmap[x][y]) + river - world.roads[x][y])


def _reconstruct_path(parents: Grid[Point], start: Point, end: Point) -> list[Point]:
    path = []
    current = end
    while True:
        path.append(current)
        if current == start:
            break
        current = parents[current[0]][current[1]]
    return path


# TODO: optimise for multiple goals
def find_path(world: World, start: Point, end: Point) -> tuple[list[Point], float]:
    reverse = False
    if start[0] > end[0]:
        reverse = True
        cache_line = (end, start)
    else:
        cache_line = (start, end)

    if cache_line in world.path_cache:
        #cache found
        if world.path_cache[cache_line][2] < world.turn - world.path_cache_timeout:
            #cache is old, recalculate
            del world.path_cache[cache_line]
        else:
            print("cache hit, age: "+str(world.turn - world.path_cache[cache_line][2])+" / "+str(world.path_cache_timeout)+" turns")
            path, cost, _ = world.path_cache[cache_line]
            if reverse:
                print("reversed chache line hit")
                path.reverse()
            return (path, cost)

    width = world.width
    height = world.height
    sx, sy = start

    pq = [(0.0, sx, sy)]

    min_distance = [[float("inf")] * width for _ in range(height)]
    min_distance[sx][sy] = 0

    parents = [[None] * width for _ in range(height)]

    while pq:
        current_cost, x, y = heapq.heappop(pq)
        if (x, y) == end:
            path = _reconstruct_path(parents, start, end)
            world.path_cache[cache_line] = (path, current_cost, world.turn)
            return path, current_cost

        neighbours = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        for nx, ny in neighbours:
            if not (0 <= nx < world.width and 0 <= ny < world.height):
                continue
            p_cost = _cost(world, nx, ny)
            new_cost = current_cost + p_cost
            if new_cost < min_distance[nx][ny]:
                min_distance[nx][ny] = new_cost
                parents[nx][ny] = (x, y)
                heapq.heappush(pq, (new_cost, nx, ny))

        neighbours_diag = [
            (x - 1, y - 1),
            (x - 1, y + 1),
            (x + 1, y - 1),
            (x + 1, y + 1),
        ]
        for nx, ny in neighbours_diag:
            if not (0 <= nx < world.width and 0 <= ny < world.height):
                continue
            p_cost = SQRT_2 * _cost(world, nx, ny)
            new_cost = current_cost + p_cost
            if new_cost < min_distance[nx][ny]:
                min_distance[nx][ny] = new_cost
                parents[nx][ny] = (x, y)
                heapq.heappush(pq, (new_cost, nx, ny))
    return [], 0
