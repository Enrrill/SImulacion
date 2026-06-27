import tkinter as tk

from src.configuracion import Estado, COLORES, ALTO_GRAFICO, ANCHO_GRAFICO, FONDO_PANEL

COLORES_SUAVES: dict[Estado, str] = {
    Estado.SANO: "#0088CC",
    Estado.INFECTADO: "#B32424",
    Estado.INMUNE: "#3D8B4F",
    Estado.MUERTO: "#7A828A",
}

MARGEN_TITULO = 20
MARGEN_SUPERIOR = 8
MARGEN_INFERIOR = 16


class Grafico:
    def __init__(self, canvas: tk.Canvas) -> None:
        self._canvas = canvas
        self._ancho = ANCHO_GRAFICO
        self._alto = ALTO_GRAFICO
        self._crear_fondo()

    def _crear_fondo(self) -> None:
        self._canvas.create_text(
            self._ancho // 2, 2,
            text="EVOLUCIÓN TEMPORAL", anchor="n",
            fill="#718093", font=("Segoe UI", 9, "bold"),
            tags="fondo",
        )

    def redimensionar(self, ancho: int, alto: int) -> None:
        if ancho == self._ancho and alto == self._alto:
            return
        self._ancho = ancho
        self._alto = alto
        self._canvas.delete("fondo")
        self._crear_fondo()

    def actualizar(
        self, historial: dict[Estado, list[int]], total_individuos: int,
        ancho: int | None = None, alto: int | None = None,
    ) -> None:
        if ancho is not None:
            self._ancho = ancho
        if alto is not None:
            self._alto = alto

        self._canvas.delete("dato")
        if total_individuos == 0:
            return

        w = self._ancho
        h = self._alto
        sup = MARGEN_SUPERIOR
        inf = h - MARGEN_INFERIOR
        rango = inf - sup

        # Líneas de referencia horizontales
        for pct, label in [(25, "25%"), (50, "50%"), (75, "75%")]:
            y = inf - (pct / 100) * rango
            self._canvas.create_line(
                0, y, w, y,
                fill="#353B48", width=1, tags=("dato", "referencia"),
            )
            self._canvas.create_text(
                4, y, text=label,
                fill="#8A95A5", anchor="w",
                font=("Segoe UI", 7), tags=("dato", "referencia"),
            )

        for estado in (Estado.SANO, Estado.INFECTADO, Estado.INMUNE, Estado.MUERTO):
            datos = historial.get(estado, [])
            if len(datos) < 2:
                continue
            pts: list[float] = []
            n = len(datos)
            for i, conteo in enumerate(datos):
                x = (i / max(n - 1, 1)) * w
                y = inf - (conteo / total_individuos) * rango
                pts.append(x)
                pts.append(y)
            pts.append(float(w))
            pts.append(float(inf))
            pts.append(0.0)
            pts.append(float(inf))
            self._canvas.create_polygon(
                *pts, fill=COLORES_SUAVES[estado], outline="", tags="dato",
            )
            self._canvas.create_line(
                *pts[:-4], fill=COLORES[estado], width=3, tags="dato",
            )

        # Leyenda
        legend_y = h - 12
        for i, (estado, label) in enumerate([
            (Estado.SANO, "Sanos"), (Estado.INFECTADO, "Infectados"),
            (Estado.INMUNE, "Inmunes"), (Estado.MUERTO, "Muertos"),
        ]):
            self._canvas.create_text(
                10 + i * 100, legend_y, text=f"● {label}",
                fill=COLORES[estado], anchor="w",
                font=("Segoe UI", 8, "bold"), tags="dato",
            )

    def limpiar(self) -> None:
        self._canvas.delete("all")
        self._crear_fondo()
