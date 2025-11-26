from miasto import Miasto
from obywatel import Obywatel
from collections.abc import Callable

class Handlarz(Obywatel):

    KOSZT_NA_JEDNOSTKE = 2
    def __init__(self):
        super().__init__()
        # self.x: int = super().miasto.x
        # self.y: int = super().miasto.y # wymagałoby wykonania algorytmu znajdowania drogogi na razie działam na odległosciach
        self.odleglosc_do_miasta_docelowego: int = 0
        self.odleglosc_od_miasta_macierzystego: int = 0
        self.predkosc: int = 10  # jednostki na turę

    def akcja(self):
        self.debug_print()
        # Tutaj będzie kolejność akcji handlarza

    def znajdz_partnera_handlowego(self):
        pass

    def kup_jak_najszybciej(self, zasob_do_kupienia: str, ilosc: int) -> tuple[Miasto, str]:
        # na razie przeszukanie różnych miast w obrębie państwa, potem po odległości byłoby to wskazane
        for miasto in self.miasto.panstwo.miasta:
            if miasto == self.miasto:
                continue
            # TODO duże uproszczenie że kupuje tylko jak miasto ma tyle zasobu ile potrzeba domyślnie powinien albo zwiedzać tyle miast aż kupi zadaną ilość albo kupić tyle ile jest dostępne i wracać
            for zasob in miasto.zasoby:
                ilosc_w_miescie, cena = miasto.zasoby[zasob]
                if zasob == zasob_do_kupienia and ilosc_w_miescie >= ilosc:
                    self.kupuj_zasoby(zasob, ilosc, cena, miasto)
                    return miasto, zasob
        return None, None

    def przelicz_cene_zasobu(self, zasob: str, miasto: object) -> float:
        ilosc, _ = miasto.zasoby[zasob]
        suma_wszystkich = sum([miasto.zasoby[z][0] for z in miasto.zasoby])
        if suma_wszystkich == 0:
            miasto.zasoby[zasob] = (ilosc, 10.0)
            return 10.0
        nowa_cena = min((suma_wszystkich/ilosc), 10)
        miasto.zasoby[zasob] = (ilosc, nowa_cena)
        return nowa_cena

    def akcja_handlarza(self, funkcja: Callable):
        # TODO do poprawy
        while self.odleglosc_do_miasta_docelowego > 0:
            self.idz_do_miasta_docelowego()
        funkcja()
        while self.odleglosc_od_miasta_macierzystego > 0:
            self.wracaj_do_miasta_macierzystego()

    def idz_do_miasta_docelowego(self):
        self.odleglosc_od_miasta_macierzystego += self.predkosc
        self.odleglosc_do_miasta_docelowego -= self.predkosc

    def wracaj_do_miasta_macierzystego(self):
        self.odleglosc_do_miasta_docelowego -= self.predkosc
        self.odleglosc_od_miasta_macierzystego -= self.predkosc

    def oblicz_koszty_podrozy(self, miasto_docelowe: Miasto) -> int:
        dx = miasto_docelowe.x - self.miasto.x
        dy = miasto_docelowe.y - self.miasto.y
        odleglosc = pow(pow(dx, 2) + pow(dy, 2), 0.5)
        return int(odleglosc)

    def oblicz_koszt_podrozy(self, miasto_docelowe: Miasto) -> int:
        odleglosc = self.oblicz_koszty_podrozy(miasto_docelowe)
        koszt = odleglosc * self.KOSZT_NA_JEDNOSTKE
        return koszt

    def planuj_podroze(self, miasto_docelowe: Miasto) -> None:
        odleglosc = self.oblicz_koszty_podrozy(miasto_docelowe)
        self.odleglosc_do_miasta_docelowego = odleglosc
        self.odleglosc_od_miasta_macierzystego = 0

    def sprzedaj_zasoby(self): # Handlarz nie sprzedaje zasobów, tylko kupuje od miasta
        pass

    def kupuj_zasoby(self, zasob: str, ilosc: int, cena: float, miasto_sprzedajace: object) -> None:
        aktualne = self.miasto.zasoby[zasob]
        aktualne_sprzedajace = miasto_sprzedajace.zasoby[zasob]

        self.miasto.zasoby[zasob] = (aktualne[0] + ilosc, aktualne[1])
        miasto_sprzedajace.zasoby[zasob] = (aktualne_sprzedajace[0] - ilosc, aktualne_sprzedajace[1])

        self.przelicz_cene_zasobu(zasob, self.miasto)
        self.przelicz_cene_zasobu(zasob, miasto_sprzedajace)

    def transportuj_zasoby(self):
        pass

    def buduj_droge(self):
        pass

    def mieszaj_kulture(self):
        pass
