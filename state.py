from army import Army
from city import City


class State:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.cities: list[City] = []
        self.armies: list[Army] = []
        self.objectives: list[object] = []
        self.ruler: object = None
        self.diplomacy: list[object] = []

    def add_city(self, city: City) -> None:
        # miasto.panstwo = self
        self.cities.append(city)

    def add_army(self, army: Army) -> None:
        self.armies.append(army)

    def action(self):
        print(f"Akcje w państwie: {self.name}")
        for m in self.cities:
            m.action()

    def tax(self):
        pass

    def declare_war(self):
        pass

    def unify_culture(self):
        pass
