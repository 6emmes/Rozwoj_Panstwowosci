from osadnik import Osadnik
from swiat import Swiat


def main() -> None:
    europa = Swiat()

    poczatkowi_osacnicy = [
        Osadnik(10, 10, 5),
        Osadnik(20, 5, 5),
        Osadnik(15, 15, 5),
        Osadnik(30, 2, 5),
        Osadnik(5, 20, 5),
    ]
    nazwy_miast = ["Warszawa", "Krakow", "Berlin", "Madryt", "Londyn"]

    for o, n in zip(poczatkowi_osacnicy, nazwy_miast):
        europa.miasta.append(o.zaloz_miasto(n))

    tury = 1_000
    for i in range(tury):
        if i % 50 == 0:
            print(f"Zasoby w turze {i}")
            for miasto in europa.miasta:
                miasto.debug_zasoby()
        europa.next_turn()


if __name__ == "__main__":
    main()
