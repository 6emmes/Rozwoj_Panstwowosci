from __future__ import annotations

import random
from typing import TYPE_CHECKING

from citizen import Citizen
from handlarz import Trader

if TYPE_CHECKING:
    from world import World


class City:

    def __init__(self, x: int, y: int, name: str, world: World) -> None:
        self.x: int = x
        self.y: int = y
        self.name: str = name
        # self.panstwo: Panstwo | None = None
        self.citizens: list[Citizen] = []
        self.table_of_weights: list[object] = []
        self.religious_value: object = None
        self.resources: dict = (
            {}
        )  # nie jestem przekonany do trzymania tego w dictcie ale na razie nie wiem jak to dobrze załatwić klasą
        self.world: World = world  # placeholder attribute
        self._randomize_initial_recources()  # Do celów testowych

    def _randomize_initial_recources(self):
        mozliwe_zasoby = ["jedzenie", "drewno", "kamien"]
        max_zasobu = 100
        for zasob in mozliwe_zasoby:
            # format zasoby[zasob] = (ilosc, cena)
            self.resources[zasob] = (
                random.randint(0, max_zasobu),
                random.uniform(1.0, 10.0),
            )
        print(f"Miasto {self.name} zostało założone")

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
        return trader

    def condtruction(self):
        pass

    def tax(self):
        pass

    def create_citizens(self):
        pass

    def action(self):
        print(f"    Akcje w mieście: {self.name}")
        for o in self.citizens:
            o.action()

    def __repr__(self):
        return f"Miasto({self.name})"
