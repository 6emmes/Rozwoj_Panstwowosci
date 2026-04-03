from typing import List, Tuple
import heapq
import numpy as np
from utils.definitions import Grid, Point
from world import World


BASE_SPEED = 2
SQRT_2 = np.sqrt(2)

CARDINAL = [(1,0), (-1,0), (0,1), (0,-1)]
DIAGONAL = [(1,1), (1,-1), (-1,1), (-1,-1)]
EIGHT = CARDINAL + DIAGONAL
EIGHT_COSTS = [1.0] * 4 + [SQRT_2] * 4

def _direction_vec(a: Point, b: Point) -> Tuple[float, float]:
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return (0.0, 0.0)
    length = np.hypot(dx, dy)
    return (dx / length, dy / length)

def _wind_factor(wind: Tuple[float, float], travel: Tuple[float, float]) -> float:
    wx, wy = wind
    wlen = np.hypot(wx, wy)
    if wlen == 0:
        return 0.5
    travel_len = np.hypot(travel[0], travel[1])
    tx, ty = travel[0] / travel_len, travel[1] / travel_len
    wind_unit = (wx / wlen, wy / wlen)
    cos_angle = wind_unit[0] * tx + wind_unit[1] * ty
    cos_angle = max(-1.0, min(1.0, cos_angle))
    # Parallel -> 0.5 perpendicular -> 1.5
    return 1.5 - abs(cos_angle - 0.2)*0.8

def is_passable(world: World, x: int, y: int) -> bool:
    return 0 <= x < world.width and 0 <= y < world.height and world.heightmap[x][y] == 0

def _reconstruct_path(parents: Grid[Point], start: Point, end: Point) -> list[Point]:
    path = []
    current = end
    while True:
        path.append(current)
        if current == start:
            break
        current = parents[current[0]][current[1]]
    return path

def find_path(world: World, start: Point, end: Point, wind: Tuple[float, float]) -> tuple[list[Point], float]:

    width = world.width
    height = world.height
    sx, sy = start
    ex, ey = end
        
    sx = int(sx/2)*2
    sy = int(sy/2)*2
    start = (sx, sy)
    ex = int(ex/2)*2
    ey = int(ey/2)*2
    end = (ex, ey)

    def heuristic(x, y):
        return (abs(x-ex)+abs(y-ey))*0.5

    pq = [(0.0 + heuristic(sx, sy), 0.0, sx, sy)] 

    min_distance = [[float("inf")] * height for _ in range(width)]
    min_distance[sx][sy] = 0

    parents = [[None] * height for _ in range(width)]
    scale = 2

    while pq:
        _, current_cost, x, y = heapq.heappop(pq)

        if current_cost != min_distance[x][y]:
            continue
                
        if (x, y) == end:
            path = _reconstruct_path(parents, start, end)
            return path, current_cost
        
        if not is_passable(world, x, y):
            if (x, y) != start:
                continue

        for (dx, dy), base_cost in zip(EIGHT, EIGHT_COSTS):
            nx, ny = x + dx*scale, y + dy*scale
            if not (0 <= nx < world.width and 0 <= ny < world.height):
                continue
            new_cost = current_cost + base_cost
            if new_cost < min_distance[nx][ny]:
                min_distance[nx][ny] = new_cost
                parents[nx][ny] = (x, y)
                priority = new_cost + heuristic(nx, ny)
                heapq.heappush(pq, (priority, new_cost, nx, ny))
    return [], 0

def sailing(world: World, start: Point, end: Point) -> Tuple[List[Point], float]:
    # cache check
    if start[0] > end[0]:
        cache_line = (end, start)
    else:
        cache_line = (start, end)

    if world.check_sailing_cache(cache_line):
        path, cost, _ = world.sailing_cache[cache_line]
        return path, cost

    # actual pathfinding

    course = _direction_vec(start, end)
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    wind = world.get_wind(midpoint)
    factor = _wind_factor(wind, course)

    path, distance = find_path(world, start, end, wind)
    cost = distance / (BASE_SPEED * factor)

    world.write_sailing_path_cache(cache_line, (path, cost, world.turn))
    return path, cost
