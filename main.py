import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from utils.sim_types import ResourceType
from world import World
from utils.display import Display

PYGAME = True


def main() -> None:
    sim_world = World()
    if PYGAME:
        display_obj = Display(sim_world)
        display_obj.pygame_init()

    sim_world.spawn_states(5, 5)

    priorities = []
    use_rates = []
    production_rates = []
    gold = []
    resources = {key: [] for key in sim_world.cities[0].resources}
    prices = {key: [] for key in sim_world.cities[0].resources}
    citizens = []

    turns = 600
    # Główna pętla symulacji
    for i in range(turns):
        if i % 100 == 0:
            print(f"turn{i}")
            sim_world.update_prices()
            print(sim_world.prices)
        priorities.append(sim_world.cities[0].priorities.copy())
        use_rates.append(sim_world.cities[0].use_rate.copy())
        production_rates.append(sim_world.cities[0].accumulation_rate)
        gold.append(sim_world.cities[0].gold)
        res = sim_world.cities[0].resources
        citizens.append(len(sim_world.cities[0].citizens))
        for key in res:
            resources[key].append(res[key][0])
            prices[key].append(res[key][1])

        sim_world.next_turn()

        if PYGAME:
            if i % 10 == 0:
                display_obj.pygame_sync()
            continue_simulation = display_obj.pygame_loop()
            if not continue_simulation:
                return

    # Wizualizacja per produkt
    plt.figure(figsize=(15, 12))

    resource_names = [rt for rt in ResourceType]
    for i, resource in enumerate(resource_names):
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
    offset = len(resource_names)

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

    for c in sim_world.cities:
        print(c.name, c.gold, len(c.citizens), c.buildings)
    print("~~~~~~ zasoby ~~~~~~")
    for c in sim_world.cities:
        print(c.name, c.accumulation_rate)


if __name__ == "__main__":
    main()
