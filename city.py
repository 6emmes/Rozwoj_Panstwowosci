from __future__ import annotations

import random
from typing import TYPE_CHECKING

from citizen import Citizen
from trader import Trader
from utils.definitions import Point

if TYPE_CHECKING:
    from world import World

RESOURCE_CRUCIALITY = {
    "jedzenie": 100,
    "drewno": 40,
    "kamien": 40
}

MAX_PRICE = 10.0
MAX_FOG = 5
RESOURCES = ["jedzenie", "drewno", "kamien"]

class City:

    def __init__(self, x: int, y: int, name: str, world: World) -> None:
        self.x: int = x
        self.y: int = y
        self.name: str = name
        # self.panstwo: Panstwo | None = None
        self.citizens: list[Citizen] = []
        self.traders: list[Trader] = [] # Trader to też citizen ale jeżeli będzie wielu citizenów to każdorazowe filtrowanie ich listy żeby traderów wyciagnąć będzie kosztowneg
        self.table_of_weights: list[object] = []
        self.religious_value: object = None
        self.gold: int = 500
        self.resources: dict = {}  # nie jestem przekonany do trzymania tego w dictcie ale na razie nie wiem jak to dobrze załatwić klasą
        self.accumulation_rate: dict = {name: 0 for name in RESOURCES}
        self.use_rate: dict = {name: 0 for name in RESOURCES}
        self.trade_efficiency: dict = {name: 0 for name in RESOURCES}
        self.world: World = world  # placeholder attribute
        self.control_init()
        self.id_init()
        print("land id: "+str(self.land_id))
        self._randomize_initial_recources()  # Do celów testowych

    def _randomize_initial_recources(self):
        possible_resources = RESOURCES
        max_resource = 100
        for zasob in possible_resources:
            # format zasoby[zasob] = (ilosc, cena)
            self.resources[zasob] = (
                random.randint(0, max_resource),
                random.uniform(1.0, 10.0),
            )
        print(f"Miasto {self.name} zostało założone")
    def control_init(self):
        self.controlled: list[Point] = []
        self.world.assign_tile_city(self.x, self.y, self)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if abs(dx) == 1 and abs(dy) == 1:
                    continue  # not important
                cur_x = self.x+dx
                cur_y = self.y+dy
                if (cur_x < 0 or cur_x >= self.world.width or cur_y < 0 or cur_y >= self.world.height):
                    continue
                self.world.assign_tile_city(cur_x, cur_y, self)

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

    def _get_resource_delta(self, resource: str) -> float:
        # Wartość zaamortyzowana w praktyce zasób dostępnt dopiero popowrocie do miasta handlarza, ale
        # żeby nie wysyłać w nieskończoność handlarzy na to samo zadanie jest dodawany
        return self.accumulation_rate[resource] + self.trade_efficiency[resource] - self.use_rate[resource]

    def _get_turns_left(self, resource: str) -> float:
        amount, _ = self.resources[resource]
        delta = self._get_resource_delta(resource)
        if delta >= 0:
            return float('inf')
        return amount / -delta

    def _get_cost_of_trade(self) -> float:
        return 1.0

    def _calculate_trade_priority(self, resource: str) -> float:
        days_left = self._get_turns_left(resource)
        if days_left == float('inf'):
            return 0.0

        cruciality = RESOURCE_CRUCIALITY[resource]
        if days_left == 0:
            days_left = 1e-6  # unikanie dzielenia przez zero
        priority = cruciality / days_left

        trip_cost = self._get_cost_of_trade()
        return priority / trip_cost

    def calcualte_use_rate(self):
        self.use_rate["jedzenie"] = len(self.citizens) * 0.1
        self.use_rate["drewno"] = len(self.citizens) * 0.05
        self.use_rate["kamien"] = len(self.citizens) * 0.05

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

    def get_resource(self, resource: str, fog_range: int = MAX_FOG) -> tuple[tuple[int, int], tuple[int, int]]:
        # Wraz z wycieraniem szlaku przez handlarza do miasta fog się zmniejszy, początkowo powinien być zależny od odległości
        amount, price = self.resources[resource]
        amount_min, amount_max = (random.randint(0, fog_range), random.randint(0, fog_range))
        price_min, price_max = (random.randint(0, fog_range), random.randint(0, fog_range))
        return (amount - amount_min, amount + amount_max), (max(price - price_min, 1), price + price_max)

    def get_gold(self, amount):
        amount_to_get = min(amount, self.gold)
        self.gold -= amount_to_get
        return amount

    def turn(self):
        self.use_resources()
        self.calculate_trade_priorities()
        priorities = self.calculate_trade_priorities()
        for resource, priority in priorities.items():
            if priority > 1.0:
                trader = None
                for t in self.traders:
                    if t.is_available():
                        trader = t
                        break
                if trader is not None:
                    amount, price = trader.buy_asap(resource, 50)
                    if amount is not None:
                        print(f"    Miasto {self.name} wysyła handlarza kupić {amount} {resource} po cenie {price}")

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
