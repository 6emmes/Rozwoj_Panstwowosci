import math
from dataclasses import dataclass
from random import randint, uniform

FUSION_STEP = 0.02
FUSION_THRESHOLD = 0.1
NO_TRAITS = 5


@dataclass
class Culture:
    # All float values should be in <0, 1> range
    traits: list[float]

    @property
    def isolationism(self) -> float:
        return self.traits[0]

    @property
    def expansionism(self) -> float:
        return self.traits[1]

    @property
    def hard_working(self) -> float:
        return self.traits[2]

    def noise(self):
        for f in self.traits:
            r = randint(-1, 1)
            f += r * FUSION_STEP

    def __repr__(self) -> str:
        traits_str = ", ".join(f"{t:.2f}" for t in self.traits)
        return f"Culture({traits_str})"


def random_culture() -> Culture:
    return Culture([uniform(0.0, 1.0) for _ in range(NO_TRAITS)])


def distance(c1: Culture, c2: Culture) -> float:
    sqrs = sum(pow(x - y, 2) for (x, y) in zip(c1.traits, c2.traits))
    return math.sqrt(sqrs)


def fuse_cultures(c1: Culture, c2: Culture):
    i = randint(0, NO_TRAITS - 1)
    delta = abs(c1.traits[i] - c2.traits[i])
    if delta <= FUSION_THRESHOLD:
        return

    fusion = FUSION_STEP * delta
    if c1.traits[i] < c2.traits[i]:
        c1.traits[i] += fusion
        c2.traits[i] -= fusion
    else:
        c1.traits[i] -= fusion
        c2.traits[i] += fusion
