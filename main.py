from world import World
from utils.display import Display
from utils.sim_types import BuildingType, ResourceType
from world import World

PYGAME = True

def main() -> None:
    sim_world = World()
    if PYGAME:
        display_obj = Display(sim_world)
        display_obj.pygame_init()

    sim_world.spawn_states(7, 5, 34)

    turns = 1_000
    # Główna pętla symulacji
    for i in range(turns):
        if i % 100 == 0:
            print(f"turn{i}")
            sim_world.update_prices()
            print(sim_world.prices)

        sim_world.next_turn()

        if PYGAME:
            if i % 10 == 0:
                display_obj.pygame_sync()
            continue_simulation = display_obj.pygame_loop()
            if not continue_simulation:
                return
    if PYGAME:
        display_obj.save()
    for c in sim_world.cities:
        print(c.name, c.gold, len(c.citizens), c.buildings)


if __name__ == "__main__":
    main()
