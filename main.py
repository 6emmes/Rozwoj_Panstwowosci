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
    city_names = ["Warszawa", "Krakow", "Berlin", "Madryt", "Londyn"]

    europe.spawn_settlers(city_names, 5)
    europe.cities[0].create_trader()
    europe.cities[0].create_trader()
    europe.cities[1].create_trader()
    europe.cities[2].create_trader()
    europe.cities[3].create_trader()

    for city in europe.cities:
        city.calcualte_use_rate()

    priorities = []
    use_rates = []
    production_rates = []
    gold = []
    resources = {key: [] for key in europe.cities[0].resources}
    prices = {key: [] for key in europe.cities[0].resources}

    turns = 2000
    # Główna pętla symulacji
    for i in range(turns):
        if i%100==0:
            print("tura: "+str(i))
        priorities.append(europe.cities[0].calculate_trade_priorities())
        use_rates.append(europe.cities[0].use_rate)
        production_rates.append(europe.cities[0].accumulation_rate)
        gold.append(europe.cities[0].gold)
        res = europe.cities[0].resources
        for key in res:
            resources[key].append(res[key][0])
            prices[key].append(res[key][1])

        europe.next_turn()

    # Wizualizacja per produkt
    plt.subplots(2, 3, figsize=(12, 6))

    for i, resource in enumerate(list(Resource)):
        priority_data = [p[resource] for p in priorities]
        use_rate_data = [u[resource] for u in use_rates]
        production_rate_data = [pr[resource] for pr in production_rates]

        df = pd.DataFrame(
            {
                "Tura": range(turns),
                "Priorytet": priority_data,
                "Wskaźnik zużycia": use_rate_data,
                "Wskaźnik produkcji": production_rate_data,
            }
        )

        plt.subplot(2, 3, i + 1)
        sns.lineplot(data=df, x="Tura", y="Priorytet", label="Priorytet")
        sns.lineplot(data=df, x="Tura", y="Wskaźnik zużycia", label="Wskaźnik zużycia")
        sns.lineplot(
            data=df, x="Tura", y="Wskaźnik produkcji", label="Wskaźnik produkcji"
        )
        plt.title(f"Zmiany priorytetu i wskaźników dla zasobu: {resource}")
        plt.xlabel("Tura")
        plt.ylabel("Wartość")
        plt.legend()

    plt.subplot(2, 3, 4)
    sns.lineplot(x=range(turns), y=gold, label="Złoto", color="gold")
    plt.title("Zmiany ilości złota w mieście")
    plt.xlabel("Tura")
    plt.ylabel("Ilość złota")
    plt.legend()

    plt.subplot(2, 3, 5)
    sns.lineplot(resources)
    plt.title("Zmiany ilości zasobów w mieście")
    plt.xlabel("Tura")
    plt.ylabel("Ilość zasobu")
    plt.legend()

    plt.subplot(2, 3, 6)
    sns.lineplot(prices)
    plt.title("Zmiany cen zasobu w czasie")
    plt.xlabel("Tura")
    plt.ylabel("Cena")
    plt.legend()

    plt.savefig("visualization/prices.png")


if __name__ == "__main__":
    main()
