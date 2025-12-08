from citizen import Citizen
from settler import Settler
from state import State
from world import World


def main() -> None:
    europe = World()
    poland = State("Polska")

    jan = Citizen()

    initial_settlers = [
        Settler(10, 10, 5, europe),
        Settler(20, 5, 5, europe),
        Settler(15, 15, 5, europe),
        Settler(30, 2, 5, europe),
        Settler(5, 20, 5, europe),
    ]
    city_names = ["Warszawa", "Krakow", "Berlin", "Madryt", "Londyn"]

    # Założenie miast początkowych
    for o, n in zip(initial_settlers, city_names):
        europe.cities.append(o.settle(n))

    trader = europe.cities[0].create_trader()

    turns = 1_000
    # Główna pętla symulacji
    for i in range(turns):
        # Wypisz debug o zasobach co 50 tur; tylko do dema
        if i % 50 == 0:
            print(f"Zasoby w turze {i}")
            for city in europe.cities:
                city.debug_resources()
        if i == 200:
            print("Kupowanie przez handlarza 60 jedzenia")
            trader.buy_asap("jedzenie", 60)
            print(f"Tura startu kupna: {i}")
        europe.next_turn()
        if trader.trader_action():
            print(f"Handlarz wrócił w {i} turze")


if __name__ == "__main__":
    main()
