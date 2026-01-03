from dataclasses import dataclass
from typing import Callable

from resources import Resource


@dataclass
class Building:
    build_cost: dict[Resource, int]
    effect: Callable[[float], float]
    build_time: int

    def __init__(
        self,
        build_cost: dict[Resource, int],
        effect: Callable[[float], float],
        build_time: int,
    ) -> None:
        self.build_cost = build_cost
        self.effect = effect
        self.build_time = build_time


@dataclass
class Mine(Building):
    def __init__(self) -> None:
        super().__init__({Resource.WOOD: 40, Resource.STONE: 10}, lambda x: 2.2 * x, 6)


@dataclass
class Farm(Building):
    def __init__(self) -> None:
        super().__init__({Resource.WOOD: 20, Resource.STONE: 10}, lambda x: 1.8 * x, 4)


@dataclass
class Woodcutter(Building):
    def __init__(self) -> None:
        super().__init__({Resource.WOOD: 10}, lambda x: 1.1 * x, 2)
