import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import resources
from citizen import Citizen
from resources import Resource
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

    europe.cities[0].create_trader()
    europe.cities[0].create_trader()

    for city in europe.cities:
        city.calcualate_use_rate()

    priorities = []
    use_rates = []
    production_rates = []
    gold = []
    resources = {key: [] for key in europe.cities[0].resources}
    prices = {key: [] for key in europe.cities[0].resources}
    citizens = []

    turns = 500
    # Główna pętla symulacji
    for i in range(turns):
        priorities.append(europe.cities[0].calculate_trade_priorities())
        use_rates.append(europe.cities[0].use_rate)
        production_rates.append(europe.cities[0].accumulation_rate)
        gold.append(europe.cities[0].gold)
        res = europe.cities[0].resources
        citizens.append(len(europe.cities[0].citizens))
        for key in res:
            resources[key].append(res[key][0])
            prices[key].append(res[key][1])

        europe.next_turn()

    # Wizualizacja per produkt
    plt.figure(figsize=(15, 12))

    for i, resource in enumerate(list(Resource)):
        priority_data = [p[resource] for p in priorities]
        use_rate_data = [u[resource] for u in use_rates]
        production_rate_data = [pr[resource] for pr in production_rates]

        df = pd.DataFrame(
            {
                "Tura": range(turns),
                "Wskaźnik produkcji": production_rate_data,
                "Priorytet": priority_data,
                "Wskaźnik zużycia": use_rate_data,
            }
        )

        plt.subplot(3, 3, i + 1)
        sns.lineplot(data=df, x="Tura", y="Priorytet", label="Priorytet")
        sns.lineplot(data=df, x="Tura", y="Wskaźnik zużycia", label="Wskaźnik zużycia")
        sns.lineplot(
            data=df, x="Tura", y="Wskaźnik produkcji", label="Wskaźnik produkcji"
        )
        plt.title(f"Zasób: {resource}")
        plt.xlabel("Tura")
        plt.ylabel("Wartość")
        plt.legend()
    offset = len(list(Resource))

    plt.subplot(3, 3, offset + 1)
    sns.lineplot(x=range(turns), y=gold, label="Złoto", color="gold")
    plt.title("Złoto")
    plt.xlabel("Tura")
    plt.ylabel("Ilość złota")
    plt.legend()

    plt.subplot(3, 3, offset + 2)
    sns.lineplot(resources)
    plt.title("Ilość zasobów")
    plt.xlabel("Tura")
    plt.ylabel("Zasób")
    plt.legend()

    plt.subplot(3, 3, offset + 3)
    sns.lineplot(prices)
    plt.title("Ceny zasobów")
    plt.xlabel("Tura")
    plt.ylabel("Cena")
    plt.legend()

    plt.subplot(3, 3, offset + 4)
    sns.lineplot(citizens)
    plt.title("Populacja")
    plt.xlabel("Tura")
    plt.ylabel("Liczba osób")

    plt.tight_layout()
    plt.savefig("visualization/prices.png")


if __name__ == "__main__":
    main()
