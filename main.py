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
    europe.cities[0].calcualte_use_rate()

    turns = 100
    # Główna pętla symulacji
    for i in range(turns):
        # Wypisz debug o zasobach co 50 tur; tylko do dema
        print(europe.cities[0].calculate_trade_priorities())
        print(europe.cities[0].recalculate_good_price('kamien'))
        europe.next_turn()
    print(europe.cities[0].traders)

if __name__ == "__main__":
    main()
