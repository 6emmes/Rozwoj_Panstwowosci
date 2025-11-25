from obywatel import Obywatel
# from miasto import Miasto

class Handlarz(Obywatel):

    def akcja(self):
        self.debug_print()
        # Tutaj będzie kolejność akcji handlarza

    def znajdz_partnera_handlowego(self):
        pass

    def kup_jak_najszybciej(self, zasob_do_kupienia: str, ilosc: int):
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

    def sprzedaj_zasoby(self):
        pass

    def kupuj_zasoby(self, zasob: str, ilosc: int, cena: float, miasto_sprzedajace: object):
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
