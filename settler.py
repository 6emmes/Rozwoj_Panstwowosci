from city import City
from world import World


class Settler:
    def __init__(self, x: int, y: int, no_citizens: int, world: World) -> None:
        self.x = x
        self.y = y
        self.no_citizens = no_citizens
        # na potrzeby linka
        self.world: World = world

    def settle(self, city_name: str):
        # TODO: dodać sprawdzanie czy miasto nie jest za blisko innego miasta
        if self.world.water[self.x][self.y] == 0:
            print("Miasto tonie!")
            return None
            #raise Exception("Miasto tonie!")
        city = City(self.x, self.y, city_name, self.world)
        for _ in range(self.no_citizens):
            city.create_citizen()
        return city
