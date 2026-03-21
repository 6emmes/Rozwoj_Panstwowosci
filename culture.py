import math
import random
from dataclasses import dataclass
from random import randint

FUSION_STEP = 0.05
FUSION_THRESHOLD = 0.1
NO_FLAVOURS = 5


@dataclass
class Culture:
    # All float values should be in <0, 1> range
    inwords_focus: float
    aggressiveness: float
    flavour: list[float]


def random_culture() -> Culture:
    return Culture(
        random.random(), random.random(), [random.random() for _ in range(NO_FLAVOURS)]
    )


def distance(c1: Culture, c2: Culture) -> float:
    sqrs = pow(c1.aggressiveness - c2.aggressiveness, 2)
    sqrs += pow(c1.inwords_focus - c2.inwords_focus, 2)
    sqrs += sum(pow(x - y, 2) for (x, y) in zip(c1.flavour, c2.flavour))
    return math.sqrt(sqrs)


def fuse_cultures(c1: Culture, c2: Culture):
    i = randint(NO_FLAVOURS)
    delta = abs(c1.flavour[i] - c2.flavour[i])
    if delta <= FUSION_THRESHOLD:
        return

    fusion = FUSION_STEP * delta / 2
    if c1.flavour[i] < c2.flavour[i]:
        c1.flavour[i] += fusion
        c2.flavour[i] -= fusion
    else:
        c1.flavour[i] -= fusion
        c2.flavour[i] += fusion
