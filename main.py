from citizen import Citizen
from settler import Settler
from state import State
from world import World
from shmemory import SharedMemoryGrid
from shmemory import SharedControlBlock
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import time

def main() -> None:
    europe = World()
    poland = State("Polska")
    shmctrl = SharedControlBlock("control")
    shmgrid = SharedMemoryGrid("road_grid", europe.width, europe.height, shmctrl)

    jan = Citizen()

    initial_settlers = [
        Settler(100, 100, 5, europe),
        Settler(120, 105, 5, europe),
        Settler(150, 150, 5, europe),
        Settler(130, 102, 5, europe),
        Settler(105, 120, 5, europe),
    ]
    city_names = ["Warszawa", "Krakow", "Berlin", "Madryt", "Londyn"]

    # Założenie miast początkowych
    for o, n in zip(initial_settlers, city_names):
        europe.cities.append(o.settle(n))

    europe.cities[0].create_trader()
    europe.cities[0].create_trader()

    for city in europe.cities:
        city.calcualte_use_rate()

    priorities = []
    use_rates = []
    production_rates = []
    gold = []
    resources = {key: [] for key in europe.cities[0].resources}
    prices = {key: [] for key in europe.cities[0].resources}

    turns = 200
    # Główna pętla symulacji
    for i in range(turns):
        # Wypisz debug o zasobach co 50 tur; tylko do dema
        priorities.append(europe.cities[0].calculate_trade_priorities())
        use_rates.append(europe.cities[0].use_rate)
        production_rates.append(europe.cities[0].accumulation_rate)
        gold.append(europe.cities[0].gold)
        res = europe.cities[0].resources
        for key in res:
            resources[key].append(res[key][0])
            prices[key].append(res[key][1])

        if shmgrid.is_ready():
            shmgrid.sync_from_python_grid(europe.roads)
            shmgrid.set_ready_flag()
            print("send")
        #time.sleep(1)
        print(i)

        europe.next_turn()

    # Wizualizacja per produkt
    plt.subplots(2, 3, figsize=(12, 6))

    for i, resource in enumerate(["jedzenie", "drewno", "kamien"]):
        priority_data = [p[resource] for p in priorities]
        use_rate_data = [u[resource] for u in use_rates]
        production_rate_data = [pr[resource] for pr in production_rates]

        df = pd.DataFrame({
            'Tura': range(turns),
            'Priorytet': priority_data,
            'Wskaźnik zużycia': use_rate_data,
            'Wskaźnik produkcji': production_rate_data
        })

        plt.subplot(2, 3, i+1)
        sns.lineplot(data=df, x='Tura', y='Priorytet', label='Priorytet')
        sns.lineplot(data=df, x='Tura', y='Wskaźnik zużycia', label='Wskaźnik zużycia')
        sns.lineplot(data=df, x='Tura', y='Wskaźnik produkcji', label='Wskaźnik produkcji')
        plt.title(f'Zmiany priorytetu i wskaźników dla zasobu: {resource}')
        plt.xlabel('Tura')
        plt.ylabel('Wartość')
        plt.legend()

    plt.subplot(2, 3, 4)
    sns.lineplot(x=range(turns), y=gold, label='Złoto', color='gold')
    plt.title('Zmiany ilości złota w mieście')
    plt.xlabel('Tura')
    plt.ylabel('Ilość złota')
    plt.legend()

    plt.subplot(2, 3, 5)
    sns.lineplot(resources)
    plt.title('Zmiany ilości zasobów w mieście')
    plt.xlabel('Tura')
    plt.ylabel('Ilość zasobu')
    plt.legend()

    plt.subplot(2, 3, 6)
    sns.lineplot(prices)
    plt.title('Zmiany cen zasobu w czasie')
    plt.xlabel('Tura')
    plt.ylabel('Cena')
    plt.legend()

    plt.show()

if __name__ == "__main__":
    main()
