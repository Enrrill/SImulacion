import tkinter as tk
from tkinter import ttk

from src.almacenamiento.manejador_csv import cargar_resultados, RUTA_RESULTADOS

COLORES_GRAFICA = {
    "Sanos": "#00A8FF",
    "Inmunes": "#2ED573",
    "Muertos": "#747D8C",
}


class AplicacionAnaliticas:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Analíticas de Simulaciones")
        self.root.geometry("950x650")
        self.root.configure(bg="#1E272E")

        estilo = ttk.Style()
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("TFrame", background="#1E272E")
        estilo.configure("TLabel", background="#1E272E", foreground="#F5F6FA", font=("Segoe UI", 12))
        estilo.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), padding=10)

        marco_ppal = ttk.Frame(self.root, padding=20)
        marco_ppal.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            marco_ppal,
            text="Promedios de Supervivencia por Configuración",
            style="Title.TLabel",
        ).pack(anchor="w")

        self.canvas = tk.Canvas(marco_ppal, bg="#11151C", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Button(marco_ppal, text="↻ Actualizar Datos", command=self.cargar_datos).pack(pady=10)

        self.cargar_datos()

    def cargar_datos(self) -> None:
        self.canvas.delete("all")
        filas = cargar_resultados(RUTA_RESULTADOS)
        if not filas:
            self.canvas.create_text(
                475, 250,
                text="No hay simulaciones registradas.\n"
                     "Corre una simulación hasta el final primero.",
                fill="white", font=("Segoe UI", 14), justify="center",
            )
            return

        grupos: dict[str, list[dict[str, float]]] = {}
        for row in filas:
            try:
                pob = float(row["Poblacion"])
                if pob == 0:
                    continue
                enfermedad = row.get("Enfermedad", "Personalizada")
                if enfermedad == "Personalizada":
                    clave = f"Personalizada\n(R:{row['Radio']} I:{row['Prob_Inf']})"
                else:
                    clave = enfermedad

                p_sanos = (float(row["Sanos"]) / pob) * 100
                p_inmunes = (float(row["Inmunes"]) / pob) * 100
                p_muertos = (float(row["Muertos"]) / pob) * 100

                if clave not in grupos:
                    grupos[clave] = []
                grupos[clave].append({
                    "Sanos": p_sanos, "Inmunes": p_inmunes,
                    "Muertos": p_muertos, "Dias": float(row["Dias"]),
                })
            except (ValueError, KeyError):
                continue

        self.dibujar_grafico(grupos)

    def dibujar_grafico(self, grupos: dict[str, list[dict[str, float]]]) -> None:
        if not grupos:
            self.canvas.create_text(
                475, 250, text="No se encontraron datos válidos.",
                fill="white", font=("Segoe UI", 14),
            )
            return

        self.root.update_idletasks()
        ancho = self.canvas.winfo_width() or 900
        alto = self.canvas.winfo_height() or 500

        num_grupos = len(grupos)
        max_ancho_barra = 40
        espacio_grupo = min(150, (ancho - 150) / num_grupos)
        ancho_barra = min(max_ancho_barra, espacio_grupo / 4)

        self.canvas.create_line(60, alto - 70, ancho - 20, alto - 70, fill="white", width=2)
        self.canvas.create_line(60, 20, 60, alto - 70, fill="white", width=2)

        for i in range(0, 101, 20):
            y = alto - 70 - (i / 100) * (alto - 100)
            self.canvas.create_line(55, y, 65, y, fill="white", width=2)
            self.canvas.create_text(40, y, text=f"{i}%", fill="white", font=("Segoe UI", 10))

        x_inicio = 60 + espacio_grupo / 2

        for i, (clave, sims) in enumerate(grupos.items()):
            prom_sanos = sum(s["Sanos"] for s in sims) / len(sims)
            prom_inmunes = sum(s["Inmunes"] for s in sims) / len(sims)
            prom_muertos = sum(s["Muertos"] for s in sims) / len(sims)

            x_centro = x_inicio + i * espacio_grupo

            for j, (nombre, valor) in enumerate(
                [("Sanos", prom_sanos), ("Inmunes", prom_inmunes), ("Muertos", prom_muertos)]
            ):
                alto_barra = (valor / 100) * (alto - 100)
                bx1 = x_centro + (j - 1.5) * ancho_barra
                by1 = alto - 70 - alto_barra
                bx2 = bx1 + ancho_barra
                by2 = alto - 70

                self.canvas.create_rectangle(bx1, by1, bx2, by2, fill=COLORES_GRAFICA[nombre], outline="")

                if valor > 3:
                    self.canvas.create_text(
                        (bx1 + bx2) / 2, by1 - 10,
                        text=f"{valor:.1f}%", fill="white", font=("Segoe UI", 9),
                    )

            texto_etiqueta = f"{clave}\n(Sims: {len(sims)})"
            self.canvas.create_text(
                x_centro, alto - 25, text=texto_etiqueta,
                fill="white", font=("Segoe UI", 10, "bold"), justify="center",
            )

        leg_x = ancho - 150
        for i, nombre in enumerate(["Sanos", "Inmunes", "Muertos"]):
            self.canvas.create_rectangle(leg_x, 20 + i * 30, leg_x + 15, 35 + i * 30, fill=COLORES_GRAFICA[nombre])
            self.canvas.create_text(
                leg_x + 25, 28 + i * 30, text=nombre,
                fill="white", anchor="w", font=("Segoe UI", 10, "bold"),
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionAnaliticas(root)
    root.mainloop()
