from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True)
class Factory:
    build_cost = {"wood": 100}
    upkeep_cost = {"stone": 5}
    build_time = 5
    worker_capacity = 10

factory_list = {
    "stone_quarry": Factory(),
    "farm": Factory(),
    "lumber_camp": Factory(),
    "marble_mine": Factory(),
}

# @dataclass(frozen=True)
# class _Building:
#     build_cost: dict[Resource, int]
#     multiplier: float
#     build_time: int


# class Building(Enum):
#     MINE = _Building({Resource.WOOD: 40, Resource.STONE: 10}, 2.2, 6)
#     FARM = _Building({Resource.WOOD: 20, Resource.STONE: 10}, 1.8, 4)
#     WOODCUTTER = _Building({Resource.WOOD: 10}, 1.1, 2)

#     @property
#     def cost(self) -> dict[Resource, int]:
#         return self.value.build_cost

#     @property
#     def build_time(self) -> int:
#         return self.value.build_time

#     @property
#     def multiplier(self) -> float:
#         return self.value.multiplier


# RES_TO_BUILDING = {
#     Resource.FOOD: Building.FARM,
#     Resource.STONE: Building.MINE,
#     Resource.WOOD: Building.WOODCUTTER,
# }
