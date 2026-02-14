from utils.sim_types import BuildingType, ResourceType


class Factory:
    build_cost: dict = None
    upkeep_cost: dict = None
    build_time: int = 5
    worker_capacity: int = 10

    def __init__(self, build_cost: dict, upkeep_cost: dict, build_time: int = 5, worker_capacity: int = 10):
        self.build_cost = build_cost
        self.upkeep_cost = upkeep_cost
        self.build_time = build_time
        self.worker_capacity = worker_capacity


factory_list: dict[BuildingType, Factory] = {
    BuildingType.STONE_QUARRY: Factory(build_cost={ResourceType.WOOD: 200}, upkeep_cost={ResourceType.STONE: 2}),
    BuildingType.FARM: Factory(build_cost={ResourceType.WOOD: 250}, upkeep_cost={ResourceType.WOOD: 2}),
    BuildingType.LUMBER_CAMP: Factory(build_cost={ResourceType.WOOD: 200}, upkeep_cost={ResourceType.STONE: 2}),
    BuildingType.MARBLE_MINE: Factory(build_cost={ResourceType.STONE: 200}, upkeep_cost={ResourceType.STONE: 2}),
}
