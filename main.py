from osadnik import Osadnik
from swiat import Swiat


def turn(swiat: Swiat):
    for miasto in swiat.miasta:
        for obywatel in miasto.obywatele:
            res, ammount = obywatel.zbierz_zasoby(
                swiat.temperature[miasto.x][miasto.y],
                swiat.heightmap[miasto.x][miasto.y],
                swiat.humidity[miasto.x][miasto.y],
            )
            miasto.zasoby[res] += ammount


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
        turn(europa)


if __name__ == "__main__":
    main()
