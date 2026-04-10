from typing import TYPE_CHECKING

from city import City

if TYPE_CHECKING:
    from world import World

from culture import ISOLATIONISM_STRENGTH, Culture
from resources import RAW_RESOURCES

if TYPE_CHECKING:
    from world import World

BASE_TARIF = 0.1


class State:
    def __init__(self, world, name: str, hue: int, namelist: list[str]) -> None:
        self.name: str = name
        self.world: World = world
        self.hue: int = hue
        self.city_names: list[str] = namelist
        self.cities: list[City] = []
        self.objectives: list[object] = []
        self.ruler: object = None
        self.diplomacy: list[object] = []
        self.settle_candidates: dict = {
            resource: (0.0, 1, 1) for resource in RAW_RESOURCES
        }
        self.budget: float = 0
        self.score: float = 0
        self.tariff: float = BASE_TARIF

    @property
    def culture(self) -> Culture:
        return self.cities[0].culture

    def update_tarrif(self):
        self.tariff += self.culture.isolationism * ISOLATIONISM_STRENGTH

    def add_city(self, city: City) -> None:
        city.state = self
        self.cities.append(city)

    def turn(self):
        for c in self.cities:
            c.turn()
            if self.world.turn % 10 == 0:
                c.recalculate_goods_prices()
            for trader in c.traders:
                trader.trader_action()
        self._turn_settle()
        self._turn_diplomacy()

    def update_settle_candidates(self, new, x, y):
        for res in new.keys():
            if new[res] > self.settle_candidates[res][0]:
                self.settle_candidates[res] = (new[res], x, y)

    def _turn_settle(self):
        if self.budget > 700:
            best_value = 0
            for res in self.settle_candidates.keys():
                value = self.settle_candidates[res][0] * self.world.prices[res]
                if value > best_value:
                    best_value = value
                    best_resource = res
            if best_value < 10:
                return
            x = self.settle_candidates[best_resource][1]
            y = self.settle_candidates[best_resource][2]
            new_city = self.world.settle(self, 2, x, y)
            if new_city is None:
                # too dense / kill candidate
                self.settle_candidates[best_resource] = (0, 0, 0)
                pass
            else:
                # new_city.gold = 500 - already in city constructor
                self.budget -= 700

    def _turn_diplomacy(self):
        pass
