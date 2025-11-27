from osadnik import Osadnik
from swiat import Swiat
from panstwo import Panstwo
from miasto import Miasto
from obywatel import Obywatel


def main() -> None:
    europa = Swiat()
    polska = Panstwo("Polska")

    jan = Obywatel()

    poczatkowi_osacnicy = [
        Osadnik(10, 10, 5, europa),
        Osadnik(20, 5, 5, europa),
        Osadnik(15, 15, 5, europa),
        Osadnik(30, 2, 5, europa),
        Osadnik(5, 20, 5, europa),
    ]
    nazwy_miast = ["Warszawa", "Krakow", "Berlin", "Madryt", "Londyn"]


    # Założenie miast początkowych
    for o, n in zip(poczatkowi_osacnicy, nazwy_miast):
        europa.miasta.append(o.zaloz_miasto(n))

    handlarz = europa.miasta[0].create_handlarz()

    tury = 1_000
    # Główna pętla symulacji
    for i in range(tury):
        # Wypisz debug o zasobach co 50 tur; tylko do dema
        if i % 50 == 0:
            print(f"Zasoby w turze {i}")
            for miasto in europa.miasta:
                miasto.debug_zasoby()
        if i == 200:
            print("Kupowanie przez handlarza 60 jedzenia")
            handlarz.kup_jak_najszybciej("jedzenie", 60)
            print(f"Tura startu kupna: {i}")
        europa.next_turn()
        if handlarz.akcja_handlarza():
            print(f"Handlarz wrócił w {i} turze")

if __name__ == "__main__":
    main()
