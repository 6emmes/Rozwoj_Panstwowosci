import heapq
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world import World

MAX_HEIGHT = 255
type Point = tuple[int, int]
type Grid[T] = list[list[T]]


def _neighbours(world: World, x: int, y: int) -> list[Point]:
    neighbours = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y - 1)]
    for dx, dy in neighbours:
        if 0 <= dx <= world.width and 0 <= dy <= world.height:
            pass
        else:
            neighbours.remove((dx, dy))
    return neighbours


def _reconstruct_path(parents: Grid[Point], start: Point, end: Point) -> list[Point]:
    path = []
    current = end
    while True:
        path.append(current)
        if current == start:
            break
        current = parents[current[0]][current[1]]
    return path


def _cost(world: World, x: int, y: int) -> float:
    if world.heightmap[x][y] < 0.4 * MAX_HEIGHT:
        return float("inf")
    river_buff = world.rivers[x][y]
    return world.heightmap[x][y] / MAX_HEIGHT - 0.4 + river_buff


# TODO: optimise for multiple goals
def find_path(world: World, start: Point, end: Point) -> tuple[list[Point], float]:
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
            return path, current_cost

        if current_cost > _cost(world, x, y):
            continue

        for dx, dy in _neighbours(world, x, y):
            p_cost = _cost(world, dx, dy)
            new_cost = current_cost + p_cost
            if new_cost < min_distance[dx][dy]:
                min_distance[dx][dy] = new_cost
                parents[dx][dy] = (x, y)
                heapq.heappush(pq, (new_cost, dx, dy))
    return [], 0
