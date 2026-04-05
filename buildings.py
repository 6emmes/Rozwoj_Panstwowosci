from abc import ABC
from dataclasses import dataclass
from typing import Callable

from utils.sim_types import BuildingType, ResourceType


@dataclass
class Building(ABC):
    build_cost: dict = None
    build_time: int = 5


@dataclass
class Factory(Building):
    upkeep_cost: dict = None
    worker_capacity: int = 10


FACTORIES: dict[BuildingType, Factory] = {
    # resource extraction
    BuildingType.STONE_QUARRY: Factory(
        build_cost={ResourceType.PLANKS: 200}, upkeep_cost={ResourceType.PLANKS: 1}
    ),
    BuildingType.FARM: Factory(
        build_cost={ResourceType.BRICKS: 200}, upkeep_cost={ResourceType.PLANKS: 1}
    ),
    BuildingType.LUMBER_CAMP: Factory(
        build_cost={ResourceType.PLANKS: 200}, upkeep_cost={}
    ),
    BuildingType.MARBLE_MINE: Factory(
        build_cost={ResourceType.STONE: 200}, upkeep_cost={ResourceType.STONE: 1, ResourceType.PLANKS: 1}
    ),
    BuildingType.SILVER_MINE: Factory(
        build_cost={ResourceType.PLANKS: 200, ResourceType.STONE: 100},
        upkeep_cost={ResourceType.STONE: 2},
    ),
    # secondary processing
    BuildingType.SAWMILL: Factory(
        build_cost={ResourceType.STONE: 200}, upkeep_cost={ResourceType.STONE: 1}
    ),
    BuildingType.KILN: Factory(
        build_cost={ResourceType.STONE: 200}, upkeep_cost={ResourceType.STONE: 1}
    ),
    # support structures
}


@dataclass
class PassiveBuilding(Building):
    upkeep_cost: dict[ResourceType, float] = None
    effect: Callable = None
    unique: bool = False
    prerequisite: BuildingType|None = None


PASSIVE_BUILDINGS: dict[BuildingType, PassiveBuilding] = {
    BuildingType.HOUSE: PassiveBuilding(
        build_cost={ResourceType.BRICKS: 250},
        upkeep_cost={ResourceType.FOOD: -0.2, ResourceType.PLANKS: 2},
        effect=lambda city: setattr(city, "pop_cap", city.pop_cap + 5),
    ),
    BuildingType.TOWN_HALL: PassiveBuilding(
        build_time=15,
        build_cost={ResourceType.BRICKS: 2000},
        upkeep_cost={ResourceType.PLANKS: 3, ResourceType.BRICKS: 3},
        effect=lambda city: setattr(city, "factory_limit", city.factory_limit + 3),
        unique=True,
    ),
    BuildingType.FORUM: PassiveBuilding(
        build_time=15,
        build_cost={ResourceType.BRICKS: 4000, ResourceType.SILVER:250},
        upkeep_cost={ResourceType.PLANKS: 5, ResourceType.BRICKS: 5},
        effect=lambda city: setattr(city, "factory_limit", city.factory_limit + 5),
        unique=True,
        prerequisite=BuildingType.TOWN_HALL,
    ),
    BuildingType.PALACE: PassiveBuilding(
        build_time=15,
        build_cost={ResourceType.BRICKS: 10000, ResourceType.SILVER:250, ResourceType.MARBLE:200},
        upkeep_cost={ResourceType.PLANKS: 15, ResourceType.BRICKS: 15},
        effect=lambda city: setattr(city, "factory_limit", city.factory_limit + 10),
        unique=True,
        prerequisite=BuildingType.FORUM,
    ),
    BuildingType.TRADING_POST: PassiveBuilding(
        build_cost={ResourceType.PLANKS: 400},
        upkeep_cost={ResourceType.BRICKS: 2},
        effect=lambda city: city.create_trader(),
        unique=True,
        prerequisite=BuildingType.TOWN_HALL,
    ),
    BuildingType.TRADING_GUILD: PassiveBuilding(
        build_cost={ResourceType.PLANKS: 500},
        upkeep_cost={ResourceType.BRICKS: 3},
        effect=lambda city: city.create_trader(),
        unique=True,
        prerequisite=BuildingType.FORUM,
    )
}
