from abc import ABC, abstractmethod

from buildings import FACTORIES
from utils.sim_types import BuildingType, ResourceType


class Resource(ABC):
    @abstractmethod
    def extract(self, world, x: int, y: int, buildings: int, workers: int) -> float:
        pass


class RawResource(ABC):
    map_layer: str | None
    factory: BuildingType | None
    human_harvesting: float
    factory_harvesting: float
    map_flat_scale: float

    def __init__(
        self,
        map_layer: str | None,
        factory: BuildingType | None,
        human_harvesting: float,
        factory_harvesting: float,
        map_flat_scale: float,
    ):
        self.map_layer = map_layer
        self.factory = factory
        self.human_harvesting = human_harvesting
        self.factory_harvesting = factory_harvesting
        self.map_flat_scale = map_flat_scale

    def extract(self, world, x: int, y: int, buildings: int, workers: int) -> float:
        if self.map_layer is not None:
            terrain_factor = float(
                world.layers[self.map_layer][y][x] * self.map_flat_scale
            )
        else:
            terrain_factor = 1.0
        if self.factory is None:
            return terrain_factor * self.human_harvesting * workers
        factory_workers = min(
            workers, buildings * FACTORIES[self.factory].worker_capacity
        )
        manual_workers = workers - factory_workers
        factory_output = self.factory_harvesting * factory_workers
        manual_output = self.human_harvesting * manual_workers
        return terrain_factor * (manual_output + factory_output)


RAW_RESOURCES: dict[ResourceType, RawResource] = {
    ResourceType.STONE: RawResource(
        map_layer=None,
        factory=BuildingType.STONE_QUARRY,
        human_harvesting=0.2,
        factory_harvesting=0.5,
        map_flat_scale=5.0,
    ),
    ResourceType.WOOD_CONI: RawResource(
        map_layer="coniferous_map",
        factory=BuildingType.LUMBER_CAMP,
        human_harvesting=0.75,
        factory_harvesting=1.2,
        map_flat_scale=5.0,
    ),
    ResourceType.WOOD_DECI: RawResource(
        map_layer="deciduous_map",
        factory=BuildingType.LUMBER_CAMP,
        human_harvesting=0.75,
        factory_harvesting=1.2,
        map_flat_scale=5.0,
    ),
    # TODO: replace with wheat, move food to secondary resources
    ResourceType.FOOD: RawResource(
        map_layer="fertility_map",
        factory=BuildingType.FARM,
        human_harvesting=0.25,
        factory_harvesting=2.0,
        map_flat_scale=4.0,
    ),
    ResourceType.MARBLE: RawResource(
        map_layer="marble_map",
        factory=BuildingType.MARBLE_MINE,
        human_harvesting=0.1,
        factory_harvesting=1.0,
        map_flat_scale=5.0,
    ),
    ResourceType.SILVER: RawResource(
        map_layer="silver_map",
        factory=BuildingType.SILVER_MINE,
        human_harvesting=0.05,
        factory_harvesting=3.0,
        map_flat_scale=5.0,
    ),
}


class ManufacturedResource(ABC):
    factory: BuildingType
    human_production: float
    factory_production: float
    input_resources: dict[ResourceType, float]
    output_scale: float

    def __init__(
        self,
        factory: BuildingType,
        human_production: float,
        factory_production: float,
        input_resources: dict[ResourceType, float],
        output_scale: float = 10.0,
    ):
        self.factory = factory
        self.human_production = human_production
        self.factory_production = factory_production
        self.input_resources = input_resources
        self.output_scale = output_scale

    def extract(
        self, world: None, x: None, y: None, buildings: int, workers: int
    ) -> float:
        factory_workers = min(
            workers, buildings * FACTORIES[self.factory].worker_capacity
        )
        manual_workers = workers - factory_workers
        factory_output = self.factory_production * factory_workers
        manual_output = self.human_production * manual_workers
        return (manual_output + factory_output) * self.output_scale


MANUFACTURED_RESOURCES: dict[ResourceType, ManufacturedResource] = {
    ResourceType.PLANKS: ManufacturedResource(
        factory=BuildingType.SAWMILL,
        human_production=0.5,
        factory_production=1.0,
        input_resources={ResourceType.WOOD_DECI: 1.0, ResourceType.WOOD_CONI: 1.0},
    ),
    ResourceType.BRICKS: ManufacturedResource(
        factory=BuildingType.KILN,
        human_production=0.5,
        factory_production=1.0,
        input_resources={ResourceType.STONE: 1.0},
    ),
}

ALL_RESOURCES = RAW_RESOURCES | MANUFACTURED_RESOURCES
