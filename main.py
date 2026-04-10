from utils.display import Display
from utils.sim_types import BuildingType, ResourceType
from world import World

PYGAME = True

def main() -> None:
    sim_world = World()
    if PYGAME:
        display_obj = Display(sim_world)
        display_obj.pygame_init()

    sim_world.spawn_states(1, 5, 67)

    turns = 1_000
    # Główna pętla symulacji
    for i in range(turns):
        if i % 100 == 0:
            print(f"turn{i}")
            sim_world.update_prices()

        sim_world.next_turn()

        if PYGAME:
            if i % 10 == 0:
                display_obj.pygame_sync()
            continue_simulation = display_obj.pygame_loop()
            if not continue_simulation:
                return
    if PYGAME:
        display_obj.save()

    print("-----------------------------------------------------------------------")
    best_state = sim_world.states[max(sim_world.states, key=lambda s: sim_world.states[s].score)]
    # best_state = next(iter(sim_world.states.values()))
    print(f"Best state: {best_state.name} {best_state.hue} with score {best_state.score}")
    c = best_state.cities[0]
    print(c.name, int(c.gold), len(c.citizens))
    for b in c.buildings.items():
        print((f"  {b[0]} : \t{b[1]}").expandtabs(35))
    print(c.building_plan)
    print(c.DEBUG_bankruptcy)
    print("-----------------------------------------------------------------------")
    marble = 0
    silver = 0
    for c in sim_world.cities:
        marble += c.resources[ResourceType.MARBLE][0]
        silver += c.resources[ResourceType.SILVER][0]
    print(f"Total marble: {marble}, Total silver: {silver}")


if __name__ == "__main__":
    main()
