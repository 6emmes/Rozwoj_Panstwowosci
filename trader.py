from __future__ import annotations

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
        self.target_city: City | None = None
        self.speed: int = 10  # jednostki na turę
        self.last_path: list[Point] = []

    def action(self):
        self.debug_print()
        # Tutaj będzie kolejność akcji handlarza

    def find_trade_partner(self):
        pass

    def buy_asap(self, good: str, amount: int) -> tuple[City, str]:
        # na razie przeszukanie różnych miast w obrębie państwa, potem po odległości byłoby to wskazane
        for city in self.city.world.cities:
            if city == self.city:
                continue
            # TODO duże uproszczenie że kupuje tylko jak city ma tyle zasobu ile potrzeba domyślnie powinien albo zwiedzać tyle miast aż kupi zadaną ilość albo kupić tyle ile jest dostępne i wracać
            for resource in city.resources:
                city_amount, _ = city.resources[resource]
                if resource == good and city_amount >= amount:
                    self.target_city = city
                    self.good_to_buy = resource
                    self.amount_of_good_to_buy = amount
                    self.plan_travel()
                    return city, resource
        return None, None

    @staticmethod
    def recalculate_good_price(good: str, city: City) -> float:
        # TODO lepszy sposób przepiczania dodatkowo nie wiem czy jest to kwestia handlarza czy miasta
        amount, _ = city.resources[good]
        sum_of_all = sum([city.resources[z][0] for z in city.resources])
        if sum_of_all == 0:
            city.resources[good] = (amount, 10.0)
            return 10.0
        new_price = min((sum_of_all / amount), 10)
        city.resources[good] = (amount, new_price)
        return new_price

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
        target_x = self.city.x
        target_y = self.city.y
        path, cost = find_path(self.city.world, (home_x, home_y), (target_x, target_y))

        self.last_path = path
        self.target_city_distance = int(cost)
        self.home_city_distance = 0

    def sell_good(self):  # Handlarz nie sprzedaje zasobów, tylko kupuje od miasta
        pass

    def buy_good(self) -> None:
        amount_s, price_s = self.target_city.resources[self.good_to_buy]
        self.target_city.resources[self.good_to_buy] = (
            amount_s - self.amount_of_good_to_buy,
            price_s,
        )
        self.target_city_distance = 0
        self.recalculate_good_price(self.good_to_buy, self.target_city)

    def unpack_good(self):
        amount_m, price_m = self.city.resources[self.good_to_buy]
        self.city.resources[self.good_to_buy] = (
            amount_m + self.amount_of_good_to_buy,
            price_m,
        )
        self.recalculate_good_price(self.good_to_buy, self.city)
        self.city.world.build_road(self.last_path)

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
