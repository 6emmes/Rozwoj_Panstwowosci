from panstwo import Panstwo
from miasto import Miasto
from obywatel import Obywatel
from swiat import Swiat


def main() -> None:
    europa = Swiat()
    polska = Panstwo("Polska")
    warszawa = Miasto("Warszawa")
    wroclaw = Miasto("Wrocław")
    poznan = Miasto("Poznań")
    jan = Obywatel()

    polska.add_miasto(warszawa)
    polska.add_miasto(wroclaw)
    polska.add_miasto(poznan)

    warszawa.create_obywatel()
    warszawa.add_obywatel(jan)

    polska.akcja()

    for miasto in polska.miasta:
        print(f"Zasoby miasta {miasto.nazwa}: {miasto.zasoby}")

    handlarz = warszawa.create_handlarz()
    print(handlarz.kup_jak_najszybciej("jedzenie", 60))

    for miasto in polska.miasta:
        print(f"Zasoby miasta {miasto.nazwa}: {miasto.zasoby}")

if __name__ == "__main__":
    main()
