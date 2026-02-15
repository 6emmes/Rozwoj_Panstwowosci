from army import Army
from city import City
from typing import TYPE_CHECKING


class State:
    def __init__(self, world, name: str, hue: int, namelist: list[str]) -> None:
        self.name: str = name
        self.world = world
        self.hue: int = hue
        self.city_names: list[str] = namelist
        self.cities: list[City] = []
        self.armies: list[Army] = []
        self.objectives: list[object] = []
        self.ruler: object = None
        self.diplomacy: list[object] = []

    def add_city(self, city: City) -> None:
        city.state = self
        self.cities.append(city)

    def add_army(self, army: Army) -> None:
        self.armies.append(army)

    def turn(self):
        for c in self.cities:
            c.turn()
            if self.world.turn % 10 == 0:
                c.recalculate_goods_prices()
            for trader in c.traders:
                trader.trader_action()
