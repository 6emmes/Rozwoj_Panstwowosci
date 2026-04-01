from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

from citizen import Citizen
from resources import Resource
from utils.log import LogEvent

if TYPE_CHECKING:
    from city import City
    from utils.definitions import Point

SPEED = 10
CAPACITY_MIN = 30
CAPACITY_MAX = 50

TURBO = False

class Trader(Citizen):
    UNIT_COST = 2
    SCAN_CITIES = 3

    def __init__(self):
        super().__init__()
        # self.x: int = super().miasto.x
        # self.y: int = super().miasto.y # wymagałoby wykonania algorytmu znajdowania drogogi na razie działam na odległosciach
        self.target_city_distance: int = 0
        self.home_city_distance: int = 0
        self.good_to_buy: Resource | None = None
        self.amount_of_good_to_buy: int = 0
        self.gold: float = 0.0
        self.capacity: int = random.randint(CAPACITY_MIN, CAPACITY_MAX)
        self.target_city: City | None = None
        self.speed: int = SPEED  # jednostki na turę
        self.last_path: list[Point] = []
        self.trade_partners: dict[
            City, int
        ] = {}  # tablica miast odwiedzonych przez handlarza zmniejsza fog, czyli znajomość ceny w dnaym mieście
        self.risk_factor: float = (
            random.random()
        )  # TODO dobrze zrobić na jakiś rozkład np normalny
        self.trade_efficiency: float = 0.0

    def action(self):
        self.debug_print()
        # Tutaj będzie kolejność akcji handlarza

    def find_trade_partner(self):
        pass

    def is_available(self):
        return self.target_city is None

    def buy_asap(
        self, good: Resource, amount: int
    ) -> tuple[float | None, float | None]:
        valid_cities = self.get_valid_targets(good)
        
        for city in valid_cities:
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
                path, cost = self.plan_travel()
                self.last_path = path
                self.target_city_distance = int(cost)
                self.home_city_distance = 0
                
                if len(self.last_path) == 0:  # Path is unavaiable
                    continue
                self.trade_efficiency = math.ceil(
                    amount_to_buy / (self.target_city_distance / self.speed)
                )
                self.city.trade_efficiency[good] += self.trade_efficiency
                return amount_to_buy, price
        return None, None

    def find_opportunity_trade(self) -> tuple[int | float | None, int | float | None]:
        from utils.pathfinder import find_path

        cities: list[City] = random.sample(self.city.world.cities, self.SCAN_CITIES)
        good: Resource = random.choice(list(self.city.resources.keys()))
        best_city: City | None = None
        best_score: float = 0
        best_amount: int = 0
        best_path: list[Point] = []
        best_cost = 0
        for city in cities:
            if city.state == self.city.state and city not in self.trade_partners.keys():
                self.trade_partners[city] = 0 # zerowy fog w kraju
            if city == self.city:
                continue
            if city in self.trade_partners:
                fog = self.trade_partners[city]
                city_amount, price = city.get_resource(good, fog)
            else:
                city_amount, price = city.get_resource(good)
            if city_amount[1] <= 0:
                continue
            city_amount = math.floor(
                city_amount[0] + (city_amount[1] - city_amount[0]) * self.risk_factor
            )
            price = math.floor(price[1] - (price[1] - price[0]) * self.risk_factor) * (1 + city.state.tariff)

            trade_amount = min(self.capacity, city_amount)

            if trade_amount <= 0:
                continue

            target_city_x = city.x
            target_city_y = city.y
            home_city_x = self.city.x
            home_city_y = self.city.y
            path, cost = find_path(
                self.city.world,
                (home_city_x, home_city_y),
                (target_city_x, target_city_y),
            )

            travel_cost = int(cost)
            good_cost = trade_amount * price

            total_cost = good_cost + travel_cost

            if total_cost > self.city.gold:
                continue

            score = trade_amount / total_cost

            if score > best_score:
                best_score = score
                best_city = city
                best_amount = trade_amount
                best_path = path
                best_cost = travel_cost
        if best_city is not None:
            self.target_city = best_city
            self.good_to_buy = good
            self.amount_of_good_to_buy = best_amount
            self.gold = self.city.get_gold(best_amount * price)
            self.last_path = best_path
            self.target_city_distance = best_cost
            self.home_city_distance = 0
            self.trade_efficiency = math.ceil(
                best_amount / (self.target_city_distance / self.speed)
            )
            self.city.trade_efficiency[good] += self.trade_efficiency
            return best_amount, price
        return None, None

    def trader_action(self) -> bool:
        if self.target_city is None:
            return False
        if self.target_city_distance > 0:
            self.go_to_target_city()
        elif self.home_city_distance > 0 > self.target_city_distance:
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

    def plan_travel(self) -> tuple[list[Point], int]:
        from utils.sailor import sailing
        if TURBO:
            from utils.turbofinder import find_path
        else:
            from utils.pathfinder import find_path

        home_x = self.city.x
        home_y = self.city.y
        target_x = self.target_city.x
        target_y = self.target_city.y
        sail_cost = float('inf')
        walk_cost = float('inf')
        
        if self.target_city.ocean_id == self.city.ocean_id:
            # zegluj
            sail_path, sail_cost = sailing(self.city.world, (home_x, home_y), (target_x, target_y))
        if self.target_city.land_id == self.city.land_id:
            walk_path, walk_cost = find_path(self.city.world, (home_x, home_y), (target_x, target_y))
        if sail_cost < walk_cost:
            cost = sail_cost
            path = sail_path
            if walk_cost < 2000:
                print(f"sailing {sail_cost} <- walking {walk_cost}")
        else:
            cost = walk_cost
            path = walk_path
            if sail_cost < 2000:
                print(f"walking {walk_cost} <- sailing {sail_cost}")

        if cost == 0:
            return
        # print(
        #     f"    Handlarz planuje podróż z miasta {self.city} do miasta {self.target_city.name} kosztem {int(cost)}"
        # )
        return path, cost

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
        self.city.world.logger.save_log(
            LogEvent(
                turn=self.city.world.turn,
                location=self.city.name,
                description=f"Handlarz dostarczył {self.amount_of_good_to_buy} {self.good_to_buy} do miasta {self.city.name}"
            )
        )

    def reset_trader(self):
        self.target_city_distance = 0
        self.home_city_distance = 0
        self.good_to_buy = None
        self.amount_of_good_to_buy = 0
        self.target_city = None

    def get_valid_targets(self, good: Resource) -> list[City]:
        valid_targets = []
        
        for city in self.city.world.cities:
            if city == self.city:
                continue

            can_reach = False
            if city.land_id == self.city.land_id:
                can_reach = True  # can walk
            elif city.land_id != self.city.land_id:
                if city.ocean_id is not None and self.city.ocean_id is not None:
                    if city.ocean_id == self.city.ocean_id:
                        can_reach = True  # can sail
            if not can_reach:
                continue
            
            # Check if city has the resource
            city_amount, _ = city.get_resource(good)
            if city_amount[0] > 0:
                valid_targets.append(city)

        valid_targets.sort(key=lambda c: self._calculate_path_cost_sqrd(c))
        return valid_targets


    def _calculate_path_cost_sqrd(self, target_city: City) -> float:
        cost = (self.city.x-target_city.x) ** 2 + (self.city.y-target_city.y) ** 2
        return cost


    def __str__(self):
        return f"Handlarz z miasta {self.city.name} (cel: {self.target_city.name if self.target_city else 'brak'}, towar: {self.good_to_buy}, ilość: {self.amount_of_good_to_buy}, złoto: {self.gold})"

    def build_road(self):
        pass

    def mix_culture(self):
        pass
