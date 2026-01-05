from dataclasses import dataclass
from enum import Enum
from typing import Callable

from resources import Resource


@dataclass(frozen=True)
class _Building:
    build_cost: dict[Resource, int]
    effect: Callable[[float], float]
    build_time: int


class Building(Enum):
    MINE = _Building({Resource.WOOD: 40, Resource.STONE: 10}, lambda x: 2.2 * x, 6)
    FARM = _Building({Resource.WOOD: 20, Resource.STONE: 10}, lambda x: 1.8 * x, 4)
    WOODCUTTER = _Building({Resource.WOOD: 10}, lambda x: 1.1 * x, 2)

    @property
    def cost(self) -> dict[Resource, int]:
        return self.value.build_cost

    @property
    def build_time(self) -> int:
        return self.value.build_time

    @property
    def multiplier(self) -> Callable[[float], float]:
        return self.value.effect
