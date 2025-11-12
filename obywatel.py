class Obywatel:

    def __init__(self) -> None:
        self.miasto: "Miasto | None" = None
        # placeholder attribute
        self.kultura: object = None

    def debug_print(self) -> None:
        city_name = self.miasto.nazwa if self.miasto else None
        print(
            f"        Obywatel, miasto: {city_name}"
        )

    def akcja(self):
        self.debug_print()
    
    def migruj(self):
        pass

    def pielgrzymkuj(self):
        pass
