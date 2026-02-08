from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True)
class Factory:
    build_cost:dict = None
    upkeep_cost:dict = None
    build_time: int = 5
    worker_capacity: int = 10

factory_list = {
    "stone_quarry": Factory(build_cost={"wood": 200}, upkeep_cost={"stone": 5}),
    "farm": Factory(build_cost={"wood": 250}, upkeep_cost={"wood": 2}),
    "lumber_camp": Factory(build_cost={"wood": 200}, upkeep_cost={"stone": 5}),
    "marble_mine": Factory(build_cost={"stone": 200}, upkeep_cost={"stone": 5}),
}