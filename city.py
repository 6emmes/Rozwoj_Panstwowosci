from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

from buildings import FACTORIES, PASSIVE_BUILDINGS, Building
from culture import Culture, random_culture
from resources import (
    ALL_RESOURCES,
    MANUFACTURED_RESOURCES,
    RAW_RESOURCES,
    RawResource,
    Resource,
)
from trader import Trader
from utils.log import (
    LogCityEstablishment,
    LogConsumption,
    LogCulture,
    LogGenericResource,
    LogPopulation,
    LogProduction,
    LogResource,
    LogTrade,
    LogBankruptcy,
    LogFamine
)
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
STARVATION_SURVIVAL_RATE = 5.0

SETTLER_SCOUTING_RANGE = (32, 128)


class City:
    def __init__(
        self, x: int, y: int, name: str, world: World, culture: Culture = None
    ) -> None:
        self.x: int = x
        self.y: int = y
        self.name: str = name
        self.citizens: int = 0
        self.basic_pop_cap = 25
        self.pop_cap = 25
        self.buildings: dict[BuildingType, int] = {build: 0 for build in BUILDINGS}
        # startowa farma żeby miasto nie umarło z głodu zanim zdąży cokolwiek zbudować
        self.buildings[BuildingType.FARM] = 1
        self.building_queue: list[tuple[object, int]] = []
        self.building_plan: BuildingType|None = None
        self.unique_buildings = []
        self.factory_limit = 8
        self.traders: list[Trader] = []
        self.table_of_weights: list[object] = []
        self.religious_value: object = None
        self.gold: int = 500
        self.resources: dict[ResourceType, float] = {
            resource: (0.0, 5.0) for resource in RESOURCES
        }
        self.accumulation_rate: dict[ResourceType, float] = {
            resource: 0.0 for resource in RESOURCES
        }
        self.use_rate: dict[ResourceType, float] = {
            resource: 0 for resource in RESOURCES
        }
        self.trade_efficiency: dict[Resource, float] = {
            resource: 0.0 for resource in RESOURCES
        }
        self.import_priorities: dict[ResourceType, float] = {
            resource: 0.0 for resource in RESOURCES
        }
        self.production_priorities: dict[ResourceType, float] = {
            resource: 0.0 for resource in RESOURCES
        }
        self.priorities: dict = {resource: 0.0 for resource in RESOURCES}
        self.settle_candidates: dict = {}
        self.culture: Culture = culture if culture is not None else random_culture()
        self.culture.noise()
        self.world: World = world  # placeholder attribute
        self.state = None
        self.DEBUG_bankruptcy = 0
        self.id_init()
        self._log_city_establishment()

    def _randomize_initial_recources(self):
        possible_resources = RESOURCES
        max_resource = 250
        for zasob in possible_resources:
            # format zasoby[zasob] = (ilosc, cena)
            self.resources[zasob] = (
                random.randint(0, max_resource),
                random.uniform(1.0, 10.0),
            )
        print(f"Miasto {self.name} zostało założone w ({self.x}, {self.y})")

    def id_init(self):
        try:
            self.land_id: float = self.world.layers["id_map"][self.x][self.y]
            if self.land_id < 0.5:
                print(f"Miasto {self.name} znajduje się na wodzie!")
                raise ValueError("City cannot be placed on water")
        except ValueError:
            a = self.land_id = self.world.layers["id_map"][self.x + 2][self.y + 2]
            b = self.land_id = self.world.layers["id_map"][self.x - 2][self.y - 2]
            self.land_id = max(a, b)

        self.ocean_id, self.ocean_pos = self.world.find_ocean((self.x, self.y))
        # if self.ocean_id is None:
        #     print(f"Miasto {self.name} nie ma dostępu do oceanu")
        # else:
        #     print(f"Miasto {self.name} ma dostęp do oceanu o id {self.ocean_id}")

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

    def create_trader(self):
        try:
            self.citizens -= 1
        except IndexError:
            raise IndexError("No citizen avaiable to swap to trader")
        trader = Trader()
        self.traders.append(trader)
        trader.city = self
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

    #plan:
        if self.building_plan:
            if resource in self.building_plan[1].build_cost:
                #we want to collect all needed resources within 10 turns
                use += self.building_plan[1].build_cost[resource]/20

        target = use * cruciality
        deficit = max(target - acc, 0.1)

        return deficit

    def _calculate_production_priority(self, resource: ResourceType) -> float:
        global_price = self.world.prices[resource]
        if resource in RAW_RESOURCES:
            map_layer = RAW_RESOURCES[resource].map_layer
            if map_layer is None:
                production_rate = 0.2
            else:
                production_rate = self.world.layers[map_layer][self.x][self.y]
            production_rate *= RAW_RESOURCES[resource].map_flat_scale
        elif resource in MANUFACTURED_RESOURCES:
            production_rate = 0
            for input in MANUFACTURED_RESOURCES[resource].input_resources:
                production_rate = (
                    max(production_rate, self.accumulation_rate[input]) / 5
                )
        return global_price * production_rate

    def calculate_use_rate(self):
        for r in RESOURCES:
            self.use_rate[r] = 0.0
        self.use_rate[ResourceType.FOOD] = self.citizens * 1.0
        for b in self.buildings:
            count = self.buildings[b]
            if count > 0 and b in FACTORIES:
                for res, rate in FACTORIES[b].upkeep_cost.items():
                    self.use_rate[res] += rate * count
            if count > 0 and b in PASSIVE_BUILDINGS:
                for res, rate in PASSIVE_BUILDINGS[b].upkeep_cost.items():
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
        self.starving_citizens = 0
        for resource, rate in self.use_rate.items():
            amount, price = self.resources[resource]
            amount -= rate
            if amount < 0:
                deficit = -amount
                emergency_cost = deficit * price
                self.gold -= emergency_cost
                if self.gold < 0 and self.state is not None:
                    needed_gold = abs(self.gold)
                    subsidy = min(needed_gold, self.state.budget)
                    if subsidy > 0:
                        self.state.budget -= subsidy
                        self.gold += subsidy
                    self.gold = 0
                if self.gold < 0:
                    unpaid_gold = -self.gold
                    unbought_amount = unpaid_gold / price

                    if resource == ResourceType.FOOD:
                        self.starving_citizens = math.ceil(unbought_amount)

                    self.gold = 0
                    self.DEBUG_bankruptcy += 1
                amount = 0
                # print(f"No {resource}")
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

    def _log(self):
        if self.world.turn % 25 != 0:
            return

        logsProd = [
            LogProduction(
                turn=self.world.turn,
                location=self.name,
                resource=acc.value,
                amount=self.accumulation_rate[acc],
            )
            for acc in self.accumulation_rate.keys()
        ]

        logsCons = [
            LogConsumption(
                turn=self.world.turn,
                location=self.name,
                resource=acc.value,
                amount=self.use_rate[acc],
            )
            for acc in self.use_rate.keys()
        ]

        logsRes = [
            LogResource(
                turn=self.world.turn,
                location=self.name,
                resource=acc.value,
                amount=self.resources[acc][0],
                price=self.resources[acc][1],
            )
            for acc in self.resources.keys()
        ]

        logsGold = [
            LogGenericResource(
                turn=self.world.turn,
                location=self.name,
                resource="gold",
                amount=self.gold,
            )
        ]

        logsPop = [
            LogPopulation(
                turn=self.world.turn, location=self.name, population=self.citizens
            )
        ]

        logsCulture = [
            LogCulture(
                turn=self.world.turn, location=self.name, traits=self.culture.traits
            )
        ]

        self.world.logger.save_logs(
            logsProd + logsCons + logsRes + logsPop + logsGold + logsCulture
        )

    def _log_city_establishment(self):
        self.world.logger.save_log_est(
            LogCityEstablishment(
                turn=self.world.turn,
                location=self.name,
                land_id=self.land_id,
                ocean_id=self.ocean_id,
                X=self.x,
                Y=self.y,
            )
        )

    def turn(self):
        if self.citizens == 0:
            return

        self.calculate_priorities()

        self._turn_trading()
        self._turn_mining()
        self._turn_building()
        self._turn_settle()
        self._turn_tax()

        self.calculate_use_rate()
        self.use_resources()

        if self.starving_citizens > 0:
            deaths = 0
            for _ in range(self.starving_citizens):
                if random.random() < (1.0 / STARVATION_SURVIVAL_RATE):
                    deaths += 1

            deaths = min(deaths, self.citizens)

            self.citizens = self.citizens - deaths

            if deaths > 0:
                self.world.logger.save_logs([
                    LogFamine(
                        turn=self.world.turn,
                        location=self.name,
                        amount=deaths
                    )
                ])

        elif self.resources[ResourceType.FOOD][0] >= POP_GROWTH_COST + BUFFER:
            self._grow_population()
        self._log()

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
                        self.world.logger.save_log(
                            LogTrade(
                                turn=self.world.turn,
                                location=self.name,
                                destination=trader.target_city.name
                                if trader.target_city
                                else None,
                                travel_time=trader.target_city_distance / trader.speed
                                if trader.target_city_distance
                                else None,
                                walking=1 if trader.target_city.land_id==self.land_id else 0,
                                resource=resource.value,
                                amount=amount,
                                price=price,
                            )
                        )

    def _turn_mining(self):
        self.unemployed = self.citizens
        farm_employed = min(self.buildings[BuildingType.FARM] * 10, self.unemployed)
        self.unemployed = self.unemployed - farm_employed

        weights_map = {res: math.log(1 + p) for res, p in self.priorities.items()}
        weights_map[ResourceType.FOOD] = 0

        total = 1e-3
        for res, w in weights_map.items():
            if res in MANUFACTURED_RESOURCES:
                if self.buildings[MANUFACTURED_RESOURCES[res].factory] == 0:
                    intput = MANUFACTURED_RESOURCES[res].input_resources
                    max_input = max([self.resources[i][0] for i in intput])
                    if max_input < self.resources[res][0]:
                        weights_map[res] = 0
                        w = 0
            total += w

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
            self.accumulation_rate[res] = (
                res_obj.extract(self.world, self.x, self.y, factory_count, workers) * 1
                + self.culture.hard_working / 2
            )

            resources, price = self.resources[res]
            price *= 1 + self.culture.avarice / 2
            self.resources[res] = (resources + self.accumulation_rate[res], price)

    def _turn_building(self):
        self._turn_building_plan()
        self._turn_building_progress()

    def _turn_building_plan(self):
        if self.building_plan is not None:
            return
        
        if self.pop_cap - self.citizens < 10:
            self.building_plan = BuildingType.HOUSE, PASSIVE_BUILDINGS[BuildingType.HOUSE]
            return
        
        factory_count = sum(self.buildings[b] for b in self.buildings if b in FACTORIES)
        factory_count += sum(1 for b in self.building_queue if b in FACTORIES)
        if factory_count < self.factory_limit:
            for res in sorted(
                RESOURCES, key=self.production_priorities.get, reverse=True
            ):
                # should be even more
                if self.production_priorities[res] < 1.0:
                    continue
                if (
                    res == ResourceType.FOOD
                    and self.buildings[BuildingType.FARM] > factory_count * 0.5
                ):
                    continue  # keep farms less than 50% of buildings
                if res in RAW_RESOURCES:
                    building = RAW_RESOURCES[res].factory
                elif res in MANUFACTURED_RESOURCES:
                    building = MANUFACTURED_RESOURCES[res].factory
                self.building_plan = building, FACTORIES[building]
                return
        else:
            if not self.building_queue:
                building = random.choice(list(PASSIVE_BUILDINGS.keys()))
                building_obj = PASSIVE_BUILDINGS[building]
                if building_obj.unique and building in self.unique_buildings:
                    return
                if building_obj.prerequisite and self.buildings[building_obj.prerequisite] == 0:
                    return
                self.building_plan = building, building_obj
                return
    
    def _turn_building_progress(self):
        if self.building_queue:
            new_queue = []
            for building, i in self.building_queue:
                if i == 0:
                    self.buildings[building] += 1
                    if building in PASSIVE_BUILDINGS and PASSIVE_BUILDINGS[building].effect:
                        PASSIVE_BUILDINGS[building].effect(self)
                        if PASSIVE_BUILDINGS[building].unique:
                            self.unique_buildings.append(building)
                else:
                    new_queue.append((building, i - 1))

            self.building_queue = new_queue
        else:
            if self.building_plan:
                cost_satisfied = True

                for r, build_cost in self.building_plan[1].build_cost.items():
                    if self.resources[r][0] < build_cost + BUFFER:
                        cost_satisfied = False


                        break
                if cost_satisfied:
                    for r, build_cost in self.building_plan[1].build_cost.items():
                        amount, price = self.resources[r]
                        self.resources[r] = (amount - build_cost, price)
                    self.building_queue.append(
                        (self.building_plan[0], self.building_plan[1].build_time)
                    )
                    self.building_plan = None
                    

    def _turn_settle(self):
        if self.world.turn % 10 > 0:  # execute only sometimes
            return
        PI = 3.14159265359
        # settle spot exploration:
        sample_angle = random.uniform(0.0, 2 * PI)
        sample_radius = random.uniform(*SETTLER_SCOUTING_RANGE) * (
            1 + self.culture.expansionism
        )
        sample_x = int(sample_radius * math.cos(sample_angle)) + self.x
        sample_y = int(sample_radius * math.sin(sample_angle)) + self.y
        if (
            sample_x < 0
            or sample_x >= self.world.width
            or sample_y < 0
            or sample_y >= self.world.height
        ):
            return
        if self.world.heightmap[sample_x][sample_y] == 0:
            return
        map_value = {resource: 0 for resource in RAW_RESOURCES}
        for res in RAW_RESOURCES:
            if RAW_RESOURCES[res].map_layer is None:
                map_value[res] = 0.25
            else:
                map_value[res] = self.world.layers[RAW_RESOURCES[res].map_layer][
                    sample_x
                ][sample_y]
                map_value[res] = map_value[res] * RAW_RESOURCES[res].map_flat_scale

        self.state.update_settle_candidates(map_value, sample_x, sample_y)

    def _grow_population(self):
        if self.unemployed > 5:
            return  # no jobs for new people
        if self.citizens < self.pop_cap:
            for _ in range(0, int(math.sqrt(self.citizens))):
                if self.resources[ResourceType.FOOD][0] >= POP_GROWTH_COST + BUFFER:
                    self.citizens += 1
                    amount, cost = self.resources[ResourceType.FOOD]
                    self.resources[ResourceType.FOOD] = amount - POP_GROWTH_COST, cost
                else:
                    return

    def _turn_tax(self):
        if self.gold < 250:
            return
        tax = (self.gold - 250) // 10
        self.gold -= tax
        self.state.budget += tax
        self.state.score += tax

    def _handle_bankruptcy_consequences(self):
        if self.gold <= 0:
            for b_type in list(self.buildings.keys()):
                if self.buildings[b_type] > 0 and b_type in FACTORIES:
                    self.buildings[b_type] -= 1

                    self.world.logger.save_logs([
                        LogBankruptcy(
                            turn=self.world.turn,
                            location=self.name
                        )
                    ])
                    break

    def __repr__(self):
        return (
            f"Miasto({self.name}, mieszkańcy: {self.citizens}), kultura: {self.culture}"
        )
