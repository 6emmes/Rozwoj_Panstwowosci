from __future__ import annotations

from typing import TYPE_CHECKING

from obywatel import Citizen

if TYPE_CHECKING:
    from miasto import City


class Trader(Citizen):

    KOSZT_NA_JEDNOSTKE = 2

    def __init__(self):
        super().__init__()
        # self.x: int = super().miasto.x
        # self.y: int = super().miasto.y # wymagałoby wykonania algorytmu znajdowania drogogi na razie działam na odległosciach
        self.odleglosc_do_miasta_docelowego: int = 0
        self.odleglosc_od_miasta_macierzystego: int = 0
        self.zasob_do_kupienia: str = ""
        self.ilosc_zasobu_do_kupienia: int = 0
        self.miasto_docelowe: City | None = None
        self.predkosc: int = 10  # jednostki na turę

    def akcja(self):
        self.debug_print()
        # Tutaj będzie kolejność akcji handlarza

    def znajdz_partnera_handlowego(self):
        pass

    def kup_jak_najszybciej(
        self, zasob_do_kupienia: str, ilosc: int
    ) -> tuple[City, str]:
        # na razie przeszukanie różnych miast w obrębie państwa, potem po odległości byłoby to wskazane
        for miasto in self.city.world.miasta:
            if miasto == self.city:
                continue
            # TODO duże uproszczenie że kupuje tylko jak miasto ma tyle zasobu ile potrzeba domyślnie powinien albo zwiedzać tyle miast aż kupi zadaną ilość albo kupić tyle ile jest dostępne i wracać
            for zasob in miasto.zasoby:
                ilosc_w_miescie, _ = miasto.zasoby[zasob]
                if zasob == zasob_do_kupienia and ilosc_w_miescie >= ilosc:
                    self.miasto_docelowe = miasto
                    self.zasob_do_kupienia = zasob
                    self.ilosc_zasobu_do_kupienia = ilosc
                    self.planuj_podroze()
                    return miasto, zasob
        return None, None

    @staticmethod
    def przelicz_cene_zasobu(zasob: str, miasto: City) -> float:
        # TODO lepszy sposób przepiczania dodatkowo nie wiem czy jest to kwestia handlarza czy miasta
        ilosc, _ = miasto.resources[zasob]
        suma_wszystkich = sum([miasto.resources[z][0] for z in miasto.resources])
        if suma_wszystkich == 0:
            miasto.resources[zasob] = (ilosc, 10.0)
            return 10.0
        nowa_cena = min((suma_wszystkich / ilosc), 10)
        miasto.resources[zasob] = (ilosc, nowa_cena)
        return nowa_cena

    def akcja_handlarza(self) -> bool:
        if self.miasto_docelowe is None:
            return False
        if self.odleglosc_do_miasta_docelowego > 0:
            self.idz_do_miasta_docelowego()
        elif (
            self.odleglosc_od_miasta_macierzystego > 0
            and self.odleglosc_do_miasta_docelowego < 0
        ):
            self.kupuj_zasoby()
        elif self.odleglosc_od_miasta_macierzystego > 0:
            self.wracaj_do_miasta_macierzystego()
        else:
            self.zdeponuj_zasoby()
            self.reset_handlarza()
            return True
        return False

    def idz_do_miasta_docelowego(self):
        self.odleglosc_od_miasta_macierzystego += self.predkosc
        self.odleglosc_do_miasta_docelowego -= self.predkosc

    def wracaj_do_miasta_macierzystego(self):
        self.odleglosc_od_miasta_macierzystego -= self.predkosc

    def oblicz_odleglosc_podrozy(self) -> int:
        dx = self.miasto_docelowe.x - self.city.x
        dy = self.miasto_docelowe.y - self.city.y
        odleglosc = pow(pow(dx, 2) + pow(dy, 2), 0.5)
        return int(odleglosc)

    def oblicz_koszt_podrozy(self) -> int:
        odleglosc = self.oblicz_odleglosc_podrozy()
        koszt = odleglosc * self.KOSZT_NA_JEDNOSTKE
        return koszt

    def planuj_podroze(self) -> None:
        odleglosc = self.oblicz_odleglosc_podrozy()
        self.odleglosc_do_miasta_docelowego = odleglosc
        self.odleglosc_od_miasta_macierzystego = 0

    def sprzedaj_zasoby(self):  # Handlarz nie sprzedaje zasobów, tylko kupuje od miasta
        pass

    def kupuj_zasoby(self) -> None:
        ilosc_s, cena_s = self.miasto_docelowe.resources[self.zasob_do_kupienia]
        self.miasto_docelowe.resources[self.zasob_do_kupienia] = (
            ilosc_s - self.ilosc_zasobu_do_kupienia,
            cena_s,
        )
        self.odleglosc_do_miasta_docelowego = 0
        self.przelicz_cene_zasobu(self.zasob_do_kupienia, self.miasto_docelowe)

    def zdeponuj_zasoby(self):
        ilosc_m, cena_m = self.city.zasoby[self.zasob_do_kupienia]
        self.city.zasoby[self.zasob_do_kupienia] = (
            ilosc_m + self.ilosc_zasobu_do_kupienia,
            cena_m,
        )
        self.przelicz_cene_zasobu(self.zasob_do_kupienia, self.city)

    def reset_handlarza(self):
        self.odleglosc_do_miasta_docelowego = 0
        self.odleglosc_od_miasta_macierzystego = 0
        self.zasob_do_kupienia = ""
        self.ilosc_zasobu_do_kupienia = 0
        self.miasto_docelowe = None

    def buduj_droge(self):
        pass

    def mieszaj_kulture(self):
        pass
