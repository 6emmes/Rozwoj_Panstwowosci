from __future__ import annotations

import random
from typing import TYPE_CHECKING

from buildings import RES_TO_BUILDING, Building
from citizen import Citizen
from resources import Resource, height_efficiency, humidity_efficiency, temp_efficiency
from trader import Trader

if TYPE_CHECKING:
    from world import World

RESOURCE_CRUCIALITY = {Resource.FOOD: 100, Resource.WOOD: 40, Resource.STONE: 40}

MAX_PRICE = 10.0
MAX_FOG = 5
RESOURCES = list(Resource)


class City:

    def __init__(self, x: int, y: int, name: str, world: World) -> None:
        self.x: int = x
        self.y: int = y
        self.name: str = name
        # self.panstwo: Panstwo | None = None
        self.citizens: list[Citizen] = []
        self.buildings: dict[Building, int] = {
            Building.FARM: 0,
            Building.MINE: 0,
            Building.WOODCUTTER: 0,
        }
        self.building_queue: list[tuple[Building, int]] = []
        self.traders: list[Trader] = (
            []
        )  # Trader to też citizen ale jeżeli będzie wielu citizenów to każdorazowe filtrowanie ich listy żeby traderów wyciagnąć będzie kosztowneg
        self.table_of_weights: list[object] = []
        self.religious_value: object = None
        self.gold: int = 500
        self.resources: dict = (
            {}
        )  # nie jestem przekonany do trzymania tego w dictcie ale na razie nie wiem jak to dobrze załatwić klasą
        self.accumulation_rate: dict = {resource: 0 for resource in RESOURCES}
        self.use_rate: dict[Resource, float] = {resource: 0 for resource in RESOURCES}
        self.trade_efficiency: dict = {resource: 0 for resource in RESOURCES}
        self.world: World = world  # placeholder attribute
        print("land id: "+str(self.land_id))
        self.id_init()
        self._randomize_initial_recources()  # Do celów testowych
        if self.world.layers['height_map'][self.x][self.y] == 0:
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
        self.land_id = self.world.layers['id_map'][self.x][self.y]
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

    def condtruction(self):
        pass

    def _get_resource_delta(self, resource: Resource) -> float:
        # Wartość zaamortyzowana w praktyce zasób dostępnt dopiero popowrocie do miasta handlarza, ale
        # żeby nie wysyłać w nieskończoność handlarzy na to samo zadanie jest dodawany
        return (
            self.accumulation_rate[resource]
            + self.trade_efficiency[resource]
            - self.use_rate[resource]
        )

    def _get_turns_left(self, resource: Resource) -> float:
        amount, _ = self.resources[resource]
        delta = self._get_resource_delta(resource)
        if delta >= 0:
            return float("inf")
        return amount / -delta

    def _get_cost_of_trade(self) -> float:
        return 1.0

    def _calculate_trade_priority(self, resource: Resource) -> float:
        days_left = self._get_turns_left(resource)
        if days_left == float("inf"):
            return 0.0

        cruciality = RESOURCE_CRUCIALITY[resource]
        if days_left == 0:
            days_left = 1e-6  # unikanie dzielenia przez zero
        priority = cruciality / days_left

        trip_cost = self._get_cost_of_trade()
        return priority / trip_cost

    def calcualte_use_rate(self):
        self.use_rate[Resource.FOOD] = len(self.citizens) * 1
        self.use_rate[Resource.WOOD] = len(self.citizens) * 0.05
        self.use_rate[Resource.STONE] = len(self.citizens) * 0.05

    def calculate_trade_priorities(self) -> dict[str, float]:
        priorities = {}
        for resource in self.resources.keys():
            priority = self._calculate_trade_priority(resource)
            priorities[resource] = priority
        return priorities

    def use_resources(self):
        for resource, rate in self.use_rate.items():
            amount, price = self.resources[resource]
            amount -= rate
            if amount < 0:
                amount = 0
            self.resources[resource] = (amount, price)

    def recalculate_good_price(self, good: str) -> float:
        # TODO lepszy sposób przepiczania dodatkowo nie wiem czy jest to kwestia handlarza czy miasta
        amount, _ = self.resources[good]
        sum_of_all = sum([self.resources[z][0] for z in self.resources])
        if amount == 0:
            self.resources[good] = (amount, MAX_PRICE)
            return MAX_PRICE
        new_price = min((sum_of_all / amount), 10)
        self.resources[good] = (amount, new_price)
        return new_price

    def recalculate_goods_prices(self):
        goods = self.resources.keys()
        for good in goods:
            self.recalculate_good_price(good)

    def get_resource(
        self, resource: str, fog_range: int = MAX_FOG
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

    def _gather_resource(
        self,
        resource: Resource,
        sqr_temperature: int,
        sqr_height: int,
        sqr_humidity: int,
    ) -> float:
        return round(
            10
            * height_efficiency(resource, sqr_height)
            * temp_efficiency(resource, sqr_temperature)
            * humidity_efficiency(resource, sqr_humidity),
            2,
        )

    def turn(self):
        self.use_resources()
        self.calculate_trade_priorities()
        priorities = self.calculate_trade_priorities()
        for res, priority in priorities.items():
            if priority > 1.0:
                trader = None
                for t in self.traders:
                    if t.is_available():
                        trader = t
                        break
                if trader is not None:
                    amount, price = trader.buy_asap(res, 50)
                    if amount is not None:
                        print(
                            f"\tMiasto {self.name} wysyła handlarza kupić {amount} {res} po cenie {price}"
                        )

        # Gathering resources
        res_deltas = {res: self._get_resource_delta(res) for res in RESOURCES}
        max_d = max(res_deltas.values())
        weights_map = {res: (max_d - d + 1) for res, d in res_deltas.items()}
        choices = random.choices(
            population=list(weights_map.keys()),
            weights=list(weights_map.values()),
            k=len(self.citizens),
        )

        self.accumulation_rate = {name: 0 for name in self.resources.keys()}
        available_buildings = self.buildings.copy()
        for res in choices:
            ammount = self._gather_resource(
                res,
                self.world.temperature[self.x][self.y],
                self.world.heightmap[self.x][self.y],
                self.world.humidity[self.x][self.y],
            )
            building = RES_TO_BUILDING[res]
            if available_buildings[building] > 0:
                ammount *= building.multiplier
                available_buildings[building] -= 1

            resources, price = self.resources[res]
            # TODO przeliczanie ceny po każdej iteracji
            self.resources[res] = (resources + ammount, price)
            self.accumulation_rate[res] += ammount

        # Planning building
        BUFFER = 10.0
        for res in sorted(RESOURCES, key=self._get_resource_delta):
            building = RES_TO_BUILDING[res]
            cost_satisfied = all(
                self.resources[r][0] >= build_cost + BUFFER
                for r, build_cost in building.cost.items()
            )
            if cost_satisfied:
                for r, build_cost in building.cost.items():
                    amount, price = self.resources[r]
                    self.resources[r] = (amount - build_cost, price)
                self.building_queue.append((building, building.build_time))
                break

        # Building
        for building, i in self.building_queue:
            if i == 0:
                self.building_queue.remove((building, i))
                self.buildings[building] += 1
            else:
                i -= 1

        # Population control
        POP_GROWTH_COST = 50.0
        if self.resources[Resource.FOOD][0] >= POP_GROWTH_COST + BUFFER:
            self.create_citizen()

    def tax(self):
        pass

    def create_citizens(self):
        pass

    def action(self):
        print(f"    Akcje w mieście: {self.name}")
        for o in self.citizens:
            o.action()

    def __repr__(self):
        return f"Miasto({self.name}, mieszkańcy: {len(self.citizens)})"
