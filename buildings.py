from dataclasses import dataclass
from utils.sim_types import BuildingType, ResourceType


@dataclass(frozen=True)
class Factory:
    build_cost: dict = None
    upkeep_cost: dict = None
    build_time: int = 5
    worker_capacity: int = 10


factory_list: dict[BuildingType, Factory] = {
    BuildingType.STONE_QUARRY: Factory(build_cost={ResourceType.WOOD: 200}, upkeep_cost={ResourceType.STONE: 5}),
    BuildingType.FARM: Factory(build_cost={ResourceType.WOOD: 250}, upkeep_cost={ResourceType.WOOD: 2}),
    BuildingType.LUMBER_CAMP: Factory(build_cost={ResourceType.WOOD: 200}, upkeep_cost={ResourceType.STONE: 5}),
    BuildingType.MARBLE_MINE: Factory(build_cost={ResourceType.STONE: 200}, upkeep_cost={ResourceType.STONE: 5}),
}
