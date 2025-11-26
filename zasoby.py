import math

MAX_VAL = 255
STONE = "kamien"
WOOD = "drewno"
FOOD = "jedzenie"


def _normal(x: int, std_dev=50, mean=MAX_VAL / 2) -> float:
    e = -0.5 * math.pow((x - mean) / std_dev, 2)
    return math.exp(e)


def height_efficiency(res: str, h: int) -> float:
    if res == STONE:
        return 0.1 + h / MAX_VAL
    elif res == WOOD:
        return 1.0
    elif res == FOOD:
        return 1.1 - h / MAX_VAL
    return 1.0


def humidity_efficiency(res: str, h: int) -> float:
    if res == STONE:
        return 1.0
    elif res == WOOD:
        return 0.1 + h / MAX_VAL
    elif res == FOOD:
        return _normal(h, 80)
    return 1.0


def temp_efficiency(res: str, t: int) -> float:
    if res == STONE:
        return 1.0
    elif res == WOOD:
        return _normal(t)
    elif res == FOOD:
        return _normal(t)
    return 1.0
