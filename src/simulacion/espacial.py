import math


class HashEspacial:
    def __init__(self, tamanio_celda: int = 30) -> None:
        self.tamanio_celda = tamanio_celda
        self._cuadricula: dict[tuple[int, int], list[int]] = {}
        self._posiciones: dict[int, tuple[float, float]] = {}

    def _celda(self, x: float, y: float) -> tuple[int, int]:
        return (int(x // self.tamanio_celda), int(y // self.tamanio_celda))

    def _celdas_en_radio(
        self, x: float, y: float, radio: float,
    ) -> set[tuple[int, int]]:
        celdas: set[tuple[int, int]] = set()
        cx_min = int((x - radio) // self.tamanio_celda)
        cx_max = int((x + radio) // self.tamanio_celda)
        cy_min = int((y - radio) // self.tamanio_celda)
        cy_max = int((y + radio) // self.tamanio_celda)
        for cx in range(cx_min, cx_max + 1):
            for cy in range(cy_min, cy_max + 1):
                celdas.add((cx, cy))
        return celdas

    def insertar(self, id_unico: int, x: float, y: float) -> None:
        self._posiciones[id_unico] = (x, y)
        celda = self._celda(x, y)
        if celda not in self._cuadricula:
            self._cuadricula[celda] = []
        self._cuadricula[celda].append(id_unico)

    def actualizar(
        self, id_unico: int,
        x_anterior: float, y_anterior: float,
        x_nuevo: float, y_nuevo: float,
    ) -> None:
        self._posiciones[id_unico] = (x_nuevo, y_nuevo)
        celda_ant = self._celda(x_anterior, y_anterior)
        celda_nue = self._celda(x_nuevo, y_nuevo)
        if celda_ant == celda_nue:
            return
        self._eliminar_de_celda(id_unico, celda_ant)
        if celda_nue not in self._cuadricula:
            self._cuadricula[celda_nue] = []
        self._cuadricula[celda_nue].append(id_unico)

    def eliminar(self, id_unico: int, x: float, y: float) -> None:
        self._posiciones.pop(id_unico, None)
        self._eliminar_de_celda(id_unico, self._celda(x, y))

    def _eliminar_de_celda(
        self, id_unico: int, celda: tuple[int, int],
    ) -> None:
        if celda in self._cuadricula:
            try:
                self._cuadricula[celda].remove(id_unico)
                if not self._cuadricula[celda]:
                    del self._cuadricula[celda]
            except ValueError:
                pass

    def consultar_radio(
        self, x: float, y: float, radio: float,
    ) -> list[int]:
        vistos: set[int] = set()
        resultado: list[int] = []
        radio_cuad = radio * radio
        for celda in self._celdas_en_radio(x, y, radio):
            for id_unico in self._cuadricula.get(celda, []):
                if id_unico in vistos:
                    continue
                vistos.add(id_unico)
                px, py = self._posiciones[id_unico]
                dx = x - px
                dy = y - py
                if dx * dx + dy * dy < radio_cuad:
                    resultado.append(id_unico)
        return resultado

    def limpiar(self) -> None:
        self._cuadricula.clear()
        self._posiciones.clear()
