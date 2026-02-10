from enum import Enum


class BuildingType(Enum):
    STONE_QUARRY = "stone_quarry"
    FARM = "farm"
    LUMBER_CAMP = "lumber_camp"
    MARBLE_MINE = "marble_mine"


class ResourceType(Enum):
    STONE = "stone"
    # Zły pomosł mieć dwie zmienne -OOD
    WOOD = "wood"
    FOOD = "food"
    MARBLE = "marble"
