import tkinter as tk

from src.configuracion import Estado, COLORES, ALTO_GRAFICO


class Grafico:
    def __init__(self, canvas: tk.Canvas) -> None:
        self._canvas = canvas

    def actualizar(
        self, historial: dict[Estado, list[int]], total_individuos: int,
    ) -> None:
        self._canvas.delete("all")
        if total_individuos == 0:
            return

        for estado in historial:
            if len(historial[estado]) < 2:
                continue
            puntos: list[float] = []
            for x, conteo in enumerate(historial[estado]):
                y = ALTO_GRAFICO - (conteo / total_individuos) * ALTO_GRAFICO
                puntos.append(float(x))
                puntos.append(y)
            if puntos:
                self._canvas.create_line(
                    *puntos, fill=COLORES[estado], width=2,
                )

    def limpiar(self) -> None:
        self._canvas.delete("all")
