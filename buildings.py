from abc import ABC
from dataclasses import dataclass

from utils.sim_types import BuildingType, ResourceType


@dataclass
class Building(ABC):
    build_cost: dict = None
    upkeep_cost: dict = None
    build_time: int = 5


@dataclass
class Factory(Building):
    worker_capacity: int = 10


FACTORIES: dict[BuildingType, Factory] = {
    # resource extraction
    BuildingType.STONE_QUARRY: Factory(
        build_cost={ResourceType.PLANKS: 200}, upkeep_cost={ResourceType.STONE: 2}
    ),
    BuildingType.FARM: Factory(
        build_cost={ResourceType.PLANKS: 250}, upkeep_cost={ResourceType.PLANKS: 2}
    ),
    BuildingType.LUMBER_CAMP: Factory(
        build_cost={ResourceType.PLANKS: 200}, upkeep_cost={ResourceType.STONE: 2}
    ),
    BuildingType.MARBLE_MINE: Factory(
        build_cost={ResourceType.STONE: 200}, upkeep_cost={ResourceType.STONE: 2}
    ),
    BuildingType.SILVER_MINE: Factory(
        build_cost={ResourceType.PLANKS: 200, ResourceType.STONE: 100},
        upkeep_cost={ResourceType.STONE: 2},
    ),
    # secondary processing
    BuildingType.SAWMILL: Factory(
        build_cost={ResourceType.STONE: 200}, upkeep_cost={ResourceType.STONE: 2}
    ),
    BuildingType.KILN: Factory(
        build_cost={ResourceType.STONE: 200}, upkeep_cost={ResourceType.STONE: 2}
    ),
    # support structures
}


@dataclass
class PassiveBuilding(Building):
    affected_resources: dict[ResourceType, float] = None
    citizen_capacity: int = 2


PASSIVE_BUILDINGS: dict[BuildingType, PassiveBuilding] = {
    BuildingType.HOUSE: PassiveBuilding(
        build_cost={ResourceType.PLANKS: 20},
        upkeep_cost={ResourceType.PLANKS: 1},
        affected_resources={ResourceType.FOOD: -0.5, ResourceType.PLANKS: 0.1},
    )
}
