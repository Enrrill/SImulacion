import tkinter as tk

from src.configuracion import Estado, COLORES, ALTO_GRAFICO, ANCHO_GRAFICO, FONDO_PANEL

COLORES_SUAVES: dict[Estado, str] = {
    Estado.SANO: "#003D5C",
    Estado.INFECTADO: "#5C1A1F",
    Estado.INMUNE: "#1A4D2A",
    Estado.MUERTO: "#3A3F45",
}

MARGEN_TITULO = 20


class Grafico:
    def __init__(self, canvas: tk.Canvas) -> None:
        self._canvas = canvas
        self._crear_fondo()

    def _crear_fondo(self) -> None:
        self._canvas.create_text(
            ANCHO_GRAFICO // 2, 2,
            text="EVOLUCIÓN TEMPORAL", anchor="n",
            fill="#718093", font=("Segoe UI", 9, "bold"),
            tags="fondo",
        )

    def actualizar(
        self, historial: dict[Estado, list[int]], total_individuos: int,
    ) -> None:
        self._canvas.delete("dato")
        if total_individuos == 0:
            return

        ancho = ANCHO_GRAFICO
        for estado in (Estado.SANO, Estado.INFECTADO, Estado.INMUNE, Estado.MUERTO):
            datos = historial.get(estado, [])
            if len(datos) < 2:
                continue
            pts: list[float] = []
            for x, conteo in enumerate(datos):
                y = ALTO_GRAFICO - (conteo / total_individuos) * (ALTO_GRAFICO - MARGEN_TITULO)
                pts.append(x)
                pts.append(y)
            pts.append(float(len(datos) - 1))
            pts.append(float(ALTO_GRAFICO))
            pts.append(0.0)
            pts.append(float(ALTO_GRAFICO))
            self._canvas.create_polygon(
                *pts, fill=COLORES_SUAVES[estado], outline="", tags="dato",
            )
            self._canvas.create_line(
                *pts[:-4], fill=COLORES[estado], width=2, tags="dato",
            )

        legend_x = 10
        legend_y = ALTO_GRAFICO - 18
        for i, (estado, label) in enumerate([
            (Estado.SANO, "Sanos"), (Estado.INFECTADO, "Infectados"),
            (Estado.INMUNE, "Inmunes"), (Estado.MUERTO, "Muertos"),
        ]):
            self._canvas.create_text(
                legend_x + i * 100, legend_y, text=f"● {label}",
                fill=COLORES[estado], anchor="w",
                font=("Segoe UI", 8, "bold"), tags="dato",
            )

    def limpiar(self) -> None:
        self._canvas.delete("all")
        self._crear_fondo()
