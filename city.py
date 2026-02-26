from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

from buildings import FACTORIES, PASSIVE_BUILDINGS
from citizen import Citizen
from resources import (
    ALL_RESOURCES,
    MANUFACTURED_RESOURCES,
    RAW_RESOURCES,
    ManufacturedResource,
    RawResource,
)
from trader import Trader
from utils.sim_types import (
    BUILDINGS,
    RESOURCES,
    BuildingType,
    ResourceType,
)

if TYPE_CHECKING:
    from world import World


# RESOURCE_CRUCIALITY = {ResourceType.FOOD: 10, ResourceType.PLANKS: 4,
#                        ResourceType.STONE: 4, ResourceType.MARBLE: 1,
#                        ResourceType.WOOD_DECI: 2, ResourceType.WOOD_CONI: 2}

MAX_PRICE = 25.0
MAX_FOG = 5

BUFFER = 50
POP_GROWTH_COST = 20


class City:
    def __init__(self, x: int, y: int, name: str, world: World) -> None:
        self.x: int = x
        self.y: int = y
        self.name: str = name
        self.citizens: list[Citizen] = []
        self.buildings: dict = {build: 0 for build in BUILDINGS}
        # startowa farma żeby miasto nie umarło z głodu zanim zdąży cokolwiek zbudować
        self.buildings[BuildingType.FARM] = 1
        self.building_queue: list[tuple[object, int]] = []
        self.traders: list[Trader] = []  # Trader to też citizen
        self.table_of_weights: list[object] = []
        self.religious_value: object = None
        self.gold: int = 500
        self.resources: dict = {resource: 0 for resource in RESOURCES}
        self.accumulation_rate: dict = {resource: 0 for resource in RESOURCES}
        self.use_rate: dict = {resource: 0 for resource in RESOURCES}
        self.trade_efficiency: dict = {resource: 0 for resource in RESOURCES}
        self.import_priorities: dict = {resource: 0.0 for resource in RESOURCES}
        self.production_priorities: dict = {resource: 0.0 for resource in RESOURCES}
        self.priorities: dict = {resource: 0.0 for resource in RESOURCES}
        self.world: World = world  # placeholder attribute
        self.id_init()
        print(f"land id: {self.land_id}")
        self._randomize_initial_recources()  # Do celów testowych
        if self.world.layers["height_map"][self.x][self.y] == 0:
            print("Miasto tonie!")

    def _randomize_initial_recources(self):
        possible_resources = RESOURCES
        max_resource = 100
        for zasob in possible_resources:
            # format zasoby[zasob] = (ilosc, cena)
            self.resources[zasob] = (
                random.randint(0, max_resource),
                random.uniform(1.0, 10.0),
            )
        print(f"Miasto {self.name} zostało założone w ({self.x}, {self.y})")

    def id_init(self):
        self.land_id = self.world.layers["id_map"][self.x][self.y]
        self.ocean_id = self.world.find_ocean((self.x, self.y))
        if self.ocean_id is None:
            print(f"Miasto {self.name} nie ma dostępu do oceanu")
        else:
            print(f"Miasto {self.name} ma dostęp do oceanu o id {self.ocean_id}")

    def add_citizen(self, citizen) -> None:
        citizen.city = self
        self.citizens.append(citizen)

    def debug_resources(self):
        rounded_resources = {
            key: (
                (round(value[0], 2), round(value[1], 2))
                if isinstance(value[0], (int, float))
                and isinstance(value[1], (int, float))
                else value
            )
            for key, value in self.resources.items()
        }
        print(f"{self.name}: {rounded_resources}")

    def create_citizen(self):
        citizen = Citizen()
        self.add_citizen(citizen)
        return citizen

    def create_trader(self):
        try:
            self.citizens.pop()
        except IndexError:
            raise IndexError("No citizen avaiable to swap to trader")
        trader = Trader()
        self.add_citizen(trader)
        self.traders.append(trader)
        return trader

    def _get_resource_delta(self, resource: RawResource) -> float:
        # Wartość zaamortyzowana w praktyce zasób dostępnt dopiero popowrocie do miasta handlarza, ale
        # żeby nie wysyłać w nieskończoność handlarzy na to samo zadanie jest dodawany
        return (
            self.accumulation_rate[resource]
            + self.trade_efficiency[resource]
            - self.use_rate[resource]
        )

    def _get_turns_left(self, resource: ResourceType) -> float:
        amount, _ = self.resources[resource]
        delta = self._get_resource_delta(resource)
        if delta >= 0:
            return float("inf")
        return amount / -delta

    def _get_cost_of_trade(self) -> float:
        return 1.0

    def _calculate_import_priority(self, resource: ResourceType) -> float:
        cruciality = 1.2  # RESOURCE_CRUCIALITY[resource]
        use = self.use_rate[resource]
        acc = self.accumulation_rate[resource]

        target = use * cruciality
        deficit = max(target - acc, 0.1)

        return deficit

    def _calculate_production_priority(self, resource: ResourceType) -> float:
        global_price = self.world.prices[resource]
        if resource in RAW_RESOURCES:
            map_layer = RAW_RESOURCES[resource].map_layer
            if map_layer is None:
                production_rate = 0.25
            else:
                production_rate = self.world.layers[map_layer][self.x][self.y]
            production_rate *= RAW_RESOURCES[resource].map_flat_scale
        elif resource in MANUFACTURED_RESOURCES:
            production_rate = 0
            for input in MANUFACTURED_RESOURCES[resource].input_resources:
                production_rate = max(production_rate, self.accumulation_rate[input])
        return global_price * production_rate

    def calculate_use_rate(self):
        for r in RESOURCES:
            self.use_rate[r] = 0.0
        self.use_rate[ResourceType.FOOD] = len(self.citizens) * 1.0
        for b in self.buildings:
            count = self.buildings[b]
            if count > 0 and b in FACTORIES:
                for res, rate in FACTORIES[b].upkeep_cost.items():
                    self.use_rate[res] += rate * count
            if count > 0 and b in PASSIVE_BUILDINGS:
                for res, rate in PASSIVE_BUILDINGS[b].affected_resources.items():
                    self.use_rate[res] += rate * count

    def calculate_import_priorities(self) -> dict[ResourceType, float]:
        for resource in self.resources.keys():
            priority = self._calculate_import_priority(resource)
            self.import_priorities[resource] = priority

    def calculate_production_priorities(self) -> dict[ResourceType, float]:
        for resource in self.resources.keys():
            priority = self._calculate_production_priority(resource)
            self.production_priorities[resource] = priority

    def calculate_priorities(self) -> dict[ResourceType, float]:
        self.calculate_import_priorities()
        self.calculate_production_priorities()
        for resource in self.resources.keys():
            self.priorities[resource] = (
                self.import_priorities[resource] + self.production_priorities[resource]
            )

    def use_resources(self):
        for resource, rate in self.use_rate.items():
            amount, price = self.resources[resource]
            amount -= rate
            if amount < 0:
                amount = 0
            self.resources[resource] = (amount, price)

    def recalculate_good_price(self, good: ResourceType) -> float:
        # old priority logic
        turns_left = self._get_turns_left(good)
        sum_of_all = sum([self.resources[z][0] for z in self.resources])
        amount, _ = self.resources[good]

        scarcity = 1 / max(turns_left, 1)
        abundance = sum_of_all / max(amount, 1)

        cruciality = 1.0  # RESOURCE_CRUCIALITY[good]
        new_price = cruciality * (scarcity + abundance) / 2
        new_price = round(new_price / 10, 1)
        new_price = min(max(new_price, 1.0), MAX_PRICE)

        self.resources[good] = (amount, new_price)
        return new_price

    def recalculate_goods_prices(self):
        goods = self.resources.keys()
        for good in goods:
            self.recalculate_good_price(good)

    def get_resource(
        self, resource: ResourceType, fog_range: int = MAX_FOG
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        # Wraz z wycieraniem szlaku przez handlarza do miasta fog się zmniejszy, początkowo powinien być zależny od odległości
        amount, price = self.resources[resource]
        amount_min, amount_max = (
            random.randint(0, fog_range),
            random.randint(0, fog_range),
        )
        price_min, price_max = (
            random.randint(0, fog_range),
            random.randint(0, fog_range),
        )
        return (amount - amount_min, amount + amount_max), (
            max(price - price_min, 1),
            price + price_max,
        )

    def get_gold(self, amount):
        amount_to_get = min(amount, self.gold)
        self.gold -= amount_to_get
        return amount

    def turn(self):
        if len(self.citizens) == 0:
            return

        self.calculate_priorities()

        self._turn_trading()
        self._turn_mining()
        self._turn_building()

        self.calcualate_use_rate()
        self.use_resources()

        # Population control
        if self.resources[ResourceType.FOOD][0] == 0:
            self.citizens.pop()
        elif self.resources[ResourceType.FOOD][0] >= POP_GROWTH_COST + BUFFER:
            self._grow_population()

    def _turn_trading(self):
        for resource, priority in self.import_priorities.items():
            if priority > 1.0:
                trader = None
                for t in self.traders:
                    if t.is_available():
                        trader = t
                        break
                if trader is not None:
                    amount, price = trader.buy_asap(resource, 50)
                    if amount is not None:
                        print(
                            f"\tMiasto {self.name} wysyła handlarza kupić {amount} {resource} po cenie {price} czas: {trader.target_city_distance / trader.speed}"
                        )

    def _turn_mining(self):
        self.unemployed = len(self.citizens)
        farm_employed = min(self.buildings[BuildingType.FARM] * 10, self.unemployed)
        self.unemployed = self.unemployed - farm_employed

        weights_map = {res: math.log(1 + p) for res, p in self.priorities.items()}
        weights_map[ResourceType.FOOD] = 0

        total = sum(weights_map.values()) + 1e-3
        weights_map = {res: p / total for res, p in weights_map.items()}

        # TODO: potentially off by one due to rounding - dont care tho
        counts = {res: int(self.unemployed * w) for res, w in weights_map.items()}

        counts[ResourceType.FOOD] = farm_employed
        self.accumulation_rate = {name: 0 for name in self.resources.keys()}
        available_buildings = self.buildings.copy()
        for res, workers in counts.items():
            if workers == 0:
                continue
            if res in RAW_RESOURCES:
                res_obj = RAW_RESOURCES[res]
            elif res in MANUFACTURED_RESOURCES:
                res_obj = MANUFACTURED_RESOURCES[res]
            factory_count = available_buildings[res_obj.factory]
            self.unemployed = self.unemployed - min(factory_count * 10, workers)
            self.accumulation_rate[res] = res_obj.extract(
                self.world, self.x, self.y, factory_count, workers
            )

            resources, price = self.resources[res]
            self.resources[res] = (resources + self.accumulation_rate[res], price)

    def _turn_building(self):
        factory_count = sum(self.buildings[b] for b in self.buildings if b in FACTORIES)
        factory_count += sum(1 for b in self.building_queue if b in FACTORIES)
        if factory_count < 8:
            for res in sorted(
                RESOURCES, key=self.production_priorities.get, reverse=True
            ):
                # should be even more
                if self.production_priorities[res] < 1.0:
                    continue
                if res in RAW_RESOURCES:
                    building = FACTORIES[RAW_RESOURCES[res].factory]
                elif res in MANUFACTURED_RESOURCES:
                    building = FACTORIES[MANUFACTURED_RESOURCES[res].factory]
                cost_satisfied = all(
                    self.resources[r][0] >= build_cost + BUFFER
                    for r, build_cost in building.build_cost.items()
                )
                if cost_satisfied:
                    for r, build_cost in building.build_cost.items():
                        amount, price = self.resources[r]
                        self.resources[r] = (amount - build_cost, price)
                    self.building_queue.append(
                        (ALL_RESOURCES[res].factory, building.build_time)
                    )
                    break

        for building in PASSIVE_BUILDINGS:
            passive_building_count = self.buildings[building]
            passive_building_count += sum(
                1 for b in self.building_queue if b[0] == building
            )
            citizens = len(self.citizens)
            if (
                passive_building_count * PASSIVE_BUILDINGS[building].citizen_capacity
                < citizens
            ):
                for _ in range(
                    0,
                    citizens
                    - passive_building_count
                    * PASSIVE_BUILDINGS[building].citizen_capacity,
                ):
                    cost_satisfied = all(
                        self.resources[r][0] >= build_cost + BUFFER
                        for r, build_cost in PASSIVE_BUILDINGS[
                            building
                        ].build_cost.items()
                    )
                    if not cost_satisfied:
                        break

                    for r, build_cost in PASSIVE_BUILDINGS[building].build_cost.items():
                        amount, price = self.resources[r]
                        self.resources[r] = (amount - build_cost, price)
                    self.building_queue.append(
                        (building, PASSIVE_BUILDINGS[building].build_time)
                    )

        # Building
        new_queue = []
        for building, i in self.building_queue:
            if i == 0:
                self.buildings[building] += 1
            else:
                new_queue.append((building, i - 1))

        self.building_queue = new_queue

    def _grow_population(self):
        for _ in range(0, int(math.sqrt(len(self.citizens)))):
            if self.resources[ResourceType.FOOD][0] >= POP_GROWTH_COST + BUFFER:
                self.create_citizen()
                amount, cost = self.resources[ResourceType.FOOD]
                self.resources[ResourceType.FOOD] = amount - POP_GROWTH_COST, cost
            else:
                return

    def __repr__(self):
        return f"Miasto({self.name}, mieszkańcy: {len(self.citizens)})"
