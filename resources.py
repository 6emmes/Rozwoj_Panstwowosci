from __future__ import annotations
import math
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from buildings import factory_list

if TYPE_CHECKING:  # pragma: no cover
    from world import World


MAX_VAL = 255


@dataclass(frozen=True)
class Resource:
    map_layer: str | None = None
    factory: str | None = None
    human_harvesting: float = 0.0
    factory_harvesting: float = 0.0
    map_flat_scale: float = 10.0

    def harvest(self, world: World, x: int, y: int, buildings: int, workers: int) -> float:
        if self.map_layer is not None:
            terrain_factor = float(world.layers[self.map_layer][y][x] * self.map_flat_scale)
        else:
            terrain_factor = 1.0
        factory_workers = min(workers, buildings * factory_list[self.factory].worker_capacity)
        manual_workers = workers - factory_workers
        factory_output = self.factory_harvesting * factory_workers
        manual_output = self.human_harvesting * manual_workers
        return terrain_factor * (manual_output + factory_output)


resource_list = {
    "stone": Resource(map_layer=None, factory="stone_quarry", human_harvesting=0.2, factory_harvesting=0.5),
    # TODO: replace with wood_deciduous, move wood to secondary resources
    "wood": Resource(map_layer="coniferous_map", factory="lumber_camp", human_harvesting=0.75, factory_harvesting=1.2, map_flat_scale=5.0),
    # TODO: replace with wheat, move food to secondary resources
    "food": Resource(map_layer="fertility_map", factory="farm", human_harvesting=0.25, factory_harvesting=2.0, map_flat_scale=7.0),
    "marble": Resource(map_layer="marble_map", factory="marble_mine", human_harvesting=0.1, factory_harvesting=1.0),
}
