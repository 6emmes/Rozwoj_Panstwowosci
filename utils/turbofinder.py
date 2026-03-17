from utils.definitions import Grid, Point
from world import World

def _straight_path(start: Point, end: Point) -> list[Point]:
    """Return a simple straight path using diagonal + cardinal moves."""
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
    """Cost is simply path length (no terrain)."""
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
            print("reversed cache line hit")
            path = list(reversed(path))
        new_cost = _evaluate_path_straight(path)
        return path, new_cost

    # actual straight-line pathfinding
    path = _straight_path(start, end)
    cost = _evaluate_path_straight(path)

    # write full path to cache
    world.write_path_cache(cache_line, (path, cost, world.turn))

    # also write partial paths to intermediate cities
    for c in world.cities:
        point = (c.x, c.y)
        if point == start or point == end:
            continue
        if point in path:
            idx = path.index(point)
            partial = path[: idx + 1]
            partial_cost = float(idx)

            if start < point:
                key = (start, point)
                to_store = partial
            else:
                key = (point, start)
                to_store = list(reversed(partial))

            world.write_path_cache(key, (to_store, partial_cost, world.turn))

    return path, cost
