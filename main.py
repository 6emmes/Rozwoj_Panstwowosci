from osadnik import Osadnik
from swiat import Swiat


def main() -> None:
    europa = Swiat()
    polska = Panstwo("Polska")
    warszawa = Miasto("Warszawa", 52, 21)
    wroclaw = Miasto("Wrocław", 30, 15)
    poznan = Miasto("Poznań", 100, 200)
    jan = Obywatel()

    poczatkowi_osacnicy = [
        Osadnik(10, 10, 5),
        Osadnik(20, 5, 5),
        Osadnik(15, 15, 5),
        Osadnik(30, 2, 5),
        Osadnik(5, 20, 5),
    ]
    nazwy_miast = ["Warszawa", "Krakow", "Berlin", "Madryt", "Londyn"]

    polska.add_miasto(warszawa)
    polska.add_miasto(wroclaw)
    polska.add_miasto(poznan)

    warszawa.create_obywatel()
    warszawa.add_obywatel(jan)
    # Założenie miast początkowych
    for o, n in zip(poczatkowi_osacnicy, nazwy_miast):
        europa.miasta.append(o.zaloz_miasto(n))

    tury = 1_000

    # Główna pętla symulacji
    for i in range(tury):
        # Wypisz debug o zasobach co 50 tur; tylko do dema
        if i % 50 == 0:
            print(f"Zasoby w turze {i}")
            for miasto in europa.miasta:
                miasto.debug_zasoby()
        europa.next_turn()

    for miasto in polska.miasta:
        print(f"Zasoby miasta {miasto.nazwa}: {miasto.zasoby}")

    handlarz = warszawa.create_handlarz()
    print(handlarz.kup_jak_najszybciej("jedzenie", 60))

    for miasto in polska.miasta:
        print(f"Zasoby miasta {miasto.nazwa}: {miasto.zasoby}")

if __name__ == "__main__":
    main()
