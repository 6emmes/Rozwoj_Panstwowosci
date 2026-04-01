import heapq

import numpy as np

from utils.definitions import Grid, Point
from world import World

SQRT_2 = np.sqrt(2)
PATH_BEAUTY = 25
PATH_COST_SCALE = 0.9


def _cost(world: World, xold: int, yold: int, x: int, y: int) -> float:
    if world.water[x][y] == 0:
        return float("inf")
    river = 2 * world.rivers[x][y]
    height = (
        1
        + (PATH_BEAUTY * (world.heightmap[x][y] - world.heightmap[xold][yold]) + 0.5)
        ** 3
    )
    if (x, y) in world.cities_map:
        height /= 2
    cost = river + height - world.roads[x][y]
    cost = max(0.1, cost * PATH_COST_SCALE)
    return cost


def _reconstruct_path(parents: Grid[Point], start: Point, end: Point) -> list[Point]:
    path = []
    current = end
    while True:
        path.append(current)
        if current == start:
            break
        current = parents[current[0]][current[1]]
    return path


def _evaluate_path(world: World, path: list[Point]) -> float:
    total_cost = 0
    oldx, oldy = path[0]
    for x, y in path[1:]:
        xdist = abs(x - oldx)
        ydist = abs(y - oldy)
        if xdist == 1 and ydist == 1:
            total_cost += _cost(world, oldx, oldy, x, y) * SQRT_2
        else:
            total_cost += _cost(world, oldx, oldy, x, y)
        oldx, oldy = x, y
    return total_cost


# TODO: optimise for multiple goals
def find_path(world: World, start: Point, end: Point) -> tuple[list[Point], float]:
    # cache check
    reverse = False
    if start[0] > end[0]:
        reverse = True
        cache_line = (end, start)
    else:
        cache_line = (start, end)

    if world.check_path_cache(cache_line):
        # cache found
        path, _, _ = world.path_cache[cache_line]
        if reverse:
            # print("reversed chache line hit")
            path.reverse()
        new_cost = _evaluate_path(world, path)
        return (path, new_cost)

    # actual pathfinding:

    city_locations = []
    for c in world.cities:
        point = (c.x, c.y)
        if point == start or point == end:
            continue
        city_locations.append((c.x, c.y))

    width = world.width
    height = world.height
    sx, sy = start

    pq = [(0.0, sx, sy)]

    min_distance = [[float("inf")] * width for _ in range(height)]
    min_distance[sx][sy] = 0

    parents = [[None] * width for _ in range(height)]

    while pq:
        current_cost, x, y = heapq.heappop(pq)
        if current_cost != min_distance[x][y]:
            continue

        if (x, y) == end:
            path = _reconstruct_path(parents, start, end)
            world.write_path_cache(cache_line, (path, current_cost, world.turn))
            return path, current_cost

        if (x, y) in city_locations:
            # third city visited, update cache:
            partial_path = _reconstruct_path(parents, start, (x, y))
            cost = min_distance[x][y]
            if start < (x, y):
                key = (start, (x, y))
                path_to_store = partial_path
            else:
                key = ((x, y), start)
                path_to_store = list(reversed(partial_path))
            world.write_path_cache(key, (path_to_store, cost, world.turn))

        neighbours = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        for nx, ny in neighbours:
            if not (0 <= nx < world.width and 0 <= ny < world.height):
                continue
            p_cost = _cost(world, x, y, nx, ny)
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
            p_cost = SQRT_2 * _cost(world, x, y, nx, ny)
            new_cost = current_cost + p_cost
            if new_cost < min_distance[nx][ny]:
                min_distance[nx][ny] = new_cost
                parents[nx][ny] = (x, y)
                heapq.heappush(pq, (new_cost, nx, ny))
    return [], 0
