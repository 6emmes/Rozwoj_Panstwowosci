import math
from typing import List, Tuple

from utils.definitions import Point
from world import World

# Base speed (units per turn) – can be tuned if needed
BASE_SPEED = 2.0

def _straight_path(start: Point, end: Point) -> list[Point]:
    path = []
    x, y = start
    ex, ey = end

    while (x, y) != (ex, ey):
        path.append((x, y))

        dx = 1 if ex > x else -1 if ex < x else 0
        dy = 1 if ey > y else -1 if ey < y else 0

        x += dx
        y += dy

    path.append(end)
    return path

def _direction_vec(a: Point, b: Point) -> Tuple[float, float]:
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return (0.0, 0.0)
    length = math.hypot(dx, dy)
    return (dx / length, dy / length)


def _wind_factor(wind: Tuple[float, float], travel: Tuple[float, float]) -> float:
    wx, wy = wind
    wlen = math.hypot(wx, wy)
    if wlen == 0:
        return 0.5
    wind_unit = (wx / wlen, wy / wlen)
    cos_angle = wind_unit[0] * travel[0] + wind_unit[1] * travel[1]
    cos_angle = max(-1.0, min(1.0, cos_angle))
    # Parallel -> 0.5 perpendicular -> 1.5
    return 1.5 - abs(cos_angle - 0.2)*0.8


def sailing(world: World, start: Point, end: Point) -> Tuple[List[Point], float]:
    # cache check
    reverse = False
    if start[0] > end[0]:
        reverse = True
        cache_line = (end, start)
    else:
        cache_line = (start, end)

    if world.check_sailing_cache(cache_line):
        cost, _ = world.sailing_cache[cache_line]
        return [], cost

    # actual pathfinding
    distance = math.hypot(end[0] - start[0], end[1] - start[1])

    # path = _straight_path(start, end)
    course = _direction_vec(start, end)
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    wind = world.get_wind(midpoint)
    factor = _wind_factor(wind, course)
    cost = distance / (BASE_SPEED * factor)

    world.write_sailing_path_cache(cache_line, (cost, world.turn))
    return [], cost
