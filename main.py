from panstwo import Panstwo
from miasto import Miasto
from obywatel import Obywatel


def main() -> None:
    polska = Panstwo("Polska")
    warszawa = Miasto("Warszawa")
    jan = Obywatel()

    polska.add_miasto(warszawa)
    warszawa.create_obywatel()
    warszawa.add_obywatel(jan)

    polska.akcja()


if __name__ == "__main__":
    main()
