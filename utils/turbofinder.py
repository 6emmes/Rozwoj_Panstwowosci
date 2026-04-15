from utils.definitions import Point
from world import World

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


def _evaluate_path_straight(path: list[Point]) -> float:
    return float(len(path) - 1)


def find_path(world: World, start: Point, end: Point) -> tuple[list[Point], float]:
    # cache check
    reverse = False
    if start[0] > end[0]:
        reverse = True
        cache_line = (end, start)
    else:
        cache_line = (start, end)

    if world.check_path_cache(cache_line):
        path, _, _ = world.path_cache[cache_line]
        if reverse:
            path = list(reversed(path))
        new_cost = _evaluate_path_straight(path)
        return path, new_cost

    # actual pathfinding
    path = _straight_path(start, end)
    cost = _evaluate_path_straight(path)

    world.write_path_cache(cache_line, (path, cost, world.turn))

    return path, cost
