from enum import Enum


class BuildingType(Enum):
    STONE_QUARRY = "stone_quarry"
    FARM = "farm"
    LUMBER_CAMP = "lumber_camp"
    MARBLE_MINE = "marble_mine"
    SILVER_MINE = "silver_mine"
    SAWMILL = "sawmill"
    KILN = "kiln"
    HOUSE = "house"


class ResourceType(Enum):
    STONE = "stone"
    # Zły pomosł mieć dwie zmienne -OOD
    FOOD = "food"
    MARBLE = "marble"
    WOOD_CONI = "wood_coni"
    WOOD_DECI = "wood_deci"
    SILVER = "silver"

    PLANKS = "planks"
    BRICKS = "bricks"


RESOURCES: list[ResourceType] = [rt for rt in ResourceType]
BUILDINGS: list[BuildingType] = [bt for bt in BuildingType]
