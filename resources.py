from dataclasses import dataclass
from buildings import factory_list
from utils.sim_types import BuildingType, ResourceType


class Resource:
    map_layer: str | None
    factory: BuildingType | None
    human_harvesting: float
    factory_harvesting: float
    map_flat_scale: float

    def __init__(self, map_layer: str | None, factory: BuildingType | None, human_harvesting: float, factory_harvesting: float, map_flat_scale: float):
        self.map_layer = map_layer
        self.factory = factory
        self.human_harvesting = human_harvesting
        self.factory_harvesting = factory_harvesting
        self.map_flat_scale = map_flat_scale

    def harvest(self, world, x: int, y: int, buildings: int, workers: int) -> float:
        if self.map_layer is not None:
            terrain_factor = float(
                world.layers[self.map_layer][y][x] * self.map_flat_scale)
        else:
            terrain_factor = 1.0
        factory_workers = min(workers, buildings *
                              factory_list[self.factory].worker_capacity)
        manual_workers = workers - factory_workers
        factory_output = self.factory_harvesting * factory_workers
        manual_output = self.human_harvesting * manual_workers
        return terrain_factor * (manual_output + factory_output)


resource_list: dict[ResourceType, Resource] = {
    ResourceType.STONE: Resource(map_layer=None, factory=BuildingType.STONE_QUARRY, human_harvesting=0.2, factory_harvesting=0.5, map_flat_scale=5.0),
    # TODO: replace with wood_conifierous, move wood to secondary resources
    ResourceType.WOOD: Resource(map_layer="coniferous_map", factory=BuildingType.LUMBER_CAMP, human_harvesting=0.75, factory_harvesting=1.2, map_flat_scale=5.0),
    # TODO: replace with wheat, move food to secondary resources
    ResourceType.FOOD: Resource(map_layer="fertility_map", factory=BuildingType.FARM, human_harvesting=0.25, factory_harvesting=2.0, map_flat_scale=5.5),
    ResourceType.MARBLE: Resource(map_layer="marble_map", factory=BuildingType.MARBLE_MINE, human_harvesting=0.1, factory_harvesting=1.0),
}
