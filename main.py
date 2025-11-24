from osadnik import Osadnik
from swiat import Swiat


def main() -> None:
    europa = Swiat()
    osadnik = Osadnik(10, 10, 10)
    europa.miasta.append(osadnik.zaloz_miasto("Warszawa"))
    # jan = Obywatel()

    # polska.add_miasto(warszawa)
    # warszawa.create_obywatel()
    # warszawa.add_obywatel(jan)

    # polska.akcja()


if __name__ == "__main__":
    main()
