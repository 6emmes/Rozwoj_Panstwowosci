from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

from citizen import Citizen

if TYPE_CHECKING:
    from city import City
    from utils.definitions import Point


class Trader(Citizen):

    UNIT_COST = 2

    def __init__(self):
        super().__init__()
        # self.x: int = super().miasto.x
        # self.y: int = super().miasto.y # wymagałoby wykonania algorytmu znajdowania drogogi na razie działam na odległosciach
        self.target_city_distance: int = 0
        self.home_city_distance: int = 0
        self.good_to_buy: str = ""
        self.amount_of_good_to_buy: int = 0
        self.gold = 0
        self.capacity = random.randint(30, 50)
        self.target_city: City | None = None
        self.speed: int = 10  # jednostki na turę
        self.last_path: list[Point] = []
        self.trade_partners: dict = (
            {}
        )  # tablica miast odwiedzonych przez handlarza zmniejsza fog, czyli znajomość ceny w dnaym mieście
        self.risk_factor = (
            random.random()
        )  # TODO dobrze zrobić na jakiś rozkład np normalny

    def action(self):
        self.debug_print()
        # Tutaj będzie kolejność akcji handlarza

    def find_trade_partner(self):
        pass

    def is_available(self):
        return self.target_city is None

    def buy_asap(self, good: str, amount: int) -> tuple[float, float]:
        # na razie przeszukanie różnych miast w obrębie państwa, potem po odległości byłoby to wskazane
        for city in self.city.world.cities:
            if city == self.city:
                continue
            if city.land_id != self.city.land_id:
                continue    #miasto jest na innym lądzie
            # TODO duże uproszczenie że kupuje tylko jak city ma tyle zasobu ile potrzeba domyślnie powinien albo zwiedzać tyle miast aż kupi zadaną ilość albo kupić tyle ile jest dostępne i wracać
            if city in self.trade_partners:
                fog = self.trade_partners[city]
                city_amount, price = city.get_resource(good, fog)
            else:
                city_amount, price = city.get_resource(good)

            city_amount = math.floor(
                city_amount[0] + (city_amount[1] - city_amount[0]) * self.risk_factor
            )
            price = math.floor(price[1] - (price[1] - price[0]) * self.risk_factor)

            if city_amount >= amount:
                amount_to_buy = min(self.capacity, amount)
                self.target_city = city
                self.good_to_buy = good
                self.amount_of_good_to_buy = amount_to_buy
                self.gold = self.city.get_gold(price * amount)
                self.plan_travel()
                self.trade_efficiency = math.ceil(
                    amount_to_buy / (self.target_city_distance / self.speed)
                )
                self.city.trade_efficiency[good] += self.trade_efficiency
                return amount_to_buy, price
        return None, None

    def trader_action(self) -> bool:
        if self.target_city is None:
            return False
        if self.target_city_distance > 0:
            self.go_to_target_city()
        elif self.home_city_distance > 0 and self.target_city_distance < 0:
            self.buy_good()
        elif self.home_city_distance > 0:
            self.go_to_home_city()
        else:
            self.unpack_good()
            self.reset_trader()
            return True
        return False

    def go_to_target_city(self):
        self.home_city_distance += self.speed
        self.target_city_distance -= self.speed

    def go_to_home_city(self):
        self.home_city_distance -= self.speed

    def calculate_travel_distance(self) -> int:
        dx = self.target_city.x - self.city.x
        dy = self.target_city.y - self.city.y
        distance = pow(pow(dx, 2) + pow(dy, 2), 0.5)
        return int(distance)

    def calculate_travel_cost(self) -> int:
        distance = self.calculate_travel_distance()
        cost = distance * self.UNIT_COST
        return cost

    def plan_travel(self) -> None:
        from utils.pathfinder import find_path

        home_x = self.city.x
        home_y = self.city.y
        target_x = self.target_city.x
        target_y = self.target_city.y
        path, cost = find_path(self.city.world, (home_x, home_y), (target_x, target_y))

        self.last_path = path
        self.target_city_distance = int(cost)
        self.home_city_distance = 0

    def sell_good(self):  # Handlarz nie sprzedaje zasobów, tylko kupuje od miasta
        pass

    def buy_good(self) -> None:
        amount_s, price_s = self.target_city.resources[self.good_to_buy]
        amount = min(
            math.floor(self.gold / price_s), self.amount_of_good_to_buy, amount_s
        )
        self.target_city.resources[self.good_to_buy] = (
            amount_s - amount,
            price_s,
        )
        paid = amount * price_s
        if paid < 0:
            print(f"amout: {amount}, price_s: {price_s}, gold: {self.gold}")
        self.target_city.gold += paid
        self.gold -= paid
        self.target_city_distance = 0
        self.amount_of_good_to_buy = amount
        self.target_city.recalculate_good_price(self.good_to_buy)

    def strengthen_trade_partner(self):
        if self.target_city in self.trade_partners:
            self.trade_partners[self.target_city] = max(
                0, self.trade_partners[self.target_city] - 1
            )
        else:
            self.trade_partners[self.target_city] = 4

    def unpack_good(self):
        amount_m, price_m = self.city.resources[self.good_to_buy]
        self.city.resources[self.good_to_buy] = (
            amount_m + self.amount_of_good_to_buy,
            price_m,
        )
        self.city.world.build_road(self.last_path)
        self.city.gold += self.gold
        self.gold = 0
        self.city.trade_efficiency[self.good_to_buy] -= self.trade_efficiency
        self.city.recalculate_good_price(self.good_to_buy)
        self.strengthen_trade_partner()
        print(
            f"    Handlarz dostarczył {self.amount_of_good_to_buy} {self.good_to_buy} do miasta {self.city.name}"
        )

    def reset_trader(self):
        self.target_city_distance = 0
        self.home_city_distance = 0
        self.good_to_buy = ""
        self.amount_of_good_to_buy = 0
        self.target_city = None

    def build_road(self):
        pass

    def mix_culture(self):
        pass
