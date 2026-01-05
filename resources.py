import math
from enum import Enum

MAX_VAL = 255


class Resource(Enum):
    STONE = "kamien"
    WOOD = "drewno"
    FOOD = "jedzenie"
    # METAL = "metal"


def _normal(x: int, std_dev=50, mean=MAX_VAL / 2) -> float:
    e = -0.5 * math.pow((x - mean) / std_dev, 2)
    return math.exp(e)


def height_efficiency(res: Resource, h: int) -> float:
    match res:
        case Resource.STONE:
            return 0.1 + h / MAX_VAL
        case Resource.WOOD:
            return 1.0
        case Resource.FOOD:
            return 1.1 - h / MAX_VAL
        case _:
            return 1.0


def humidity_efficiency(res: Resource, h: int) -> float:
    match res:
        case Resource.STONE:
            return 1.0
        case Resource.WOOD:
            return 0.1 + h / MAX_VAL
        case Resource.FOOD:
            return _normal(h, 80)
        case _:
            return 1.0


def temp_efficiency(res: Resource, t: int) -> float:
    match res:
        case Resource.STONE:
            return 1.0
        case Resource.WOOD:
            return _normal(t)
        case Resource.FOOD:
            return _normal(t)
        case _:
            return 1.0
