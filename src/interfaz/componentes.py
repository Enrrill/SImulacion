import tkinter as tk
from tkinter import ttk
from typing import Callable

from src.configuracion import FONDO_PANEL, COLOR_TEXTO, FONDO_OSCURO, PRESETS_ENFERMEDADES


class SliderEtiquetado(ttk.Frame):
    def __init__(
        self, master: tk.Widget, etiqueta: str,
        variable: tk.Variable, minimo: float, maximo: float,
        resolucion: float, formato: str = "entero",
    ) -> None:
        super().__init__(master)
        self.configure(style="Dark.TFrame")
        self.pack(fill=tk.X, padx=15, pady=8)

        self._var_texto = tk.StringVar()
        self._variable = variable
        self._etiqueta = etiqueta
        self._formato = formato

        def actualizar_texto(*args: object) -> None:
            val = variable.get()
            if self._formato == "porcentaje":
                self._var_texto.set(f"{self._etiqueta}: {val * 100:.2f}%")
            elif self._formato == "decimal":
                self._var_texto.set(f"{self._etiqueta}: {val:.4f}")
            else:
                self._var_texto.set(f"{self._etiqueta}: {int(val)}")

        variable.trace_add("write", actualizar_texto)
        actualizar_texto()

        ttk.Label(
            self, textvariable=self._var_texto,
            font=("Segoe UI", 10, "bold"), foreground="#718093",
        ).pack(anchor="w")

        self.scale = ttk.Scale(
            self, variable=variable, from_=minimo, to=maximo,
            orient=tk.HORIZONTAL,
        )
        self.scale.pack(fill=tk.X, pady=(5, 0))

    def configurar_rango(self, max_val: float) -> None:
        self.scale.config(to=max_val)


class SelectorEnfermedad(ttk.Frame):
    def __init__(
        self, master: tk.Widget,
        al_seleccionar: Callable[[], None],
    ) -> None:
        super().__init__(master)
        self.configure(style="Dark.TFrame")
        self.pack(pady=(15, 0), fill=tk.X, padx=15)

        ttk.Label(self, text="Seleccionar Enfermedad:").pack(anchor="w")
        self.combo = ttk.Combobox(
            self, values=list(PRESETS_ENFERMEDADES.keys()),
            state="readonly", font=("Segoe UI", 10),
        )
        self.combo.set("Personalizada")
        self.combo.pack(fill=tk.X, pady=(5, 0))
        self.combo.bind("<<ComboboxSelected>>", lambda _: al_seleccionar())


class BotoneraControl(ttk.Frame):
    def __init__(
        self, master: tk.Widget,
        al_iniciar: Callable[[], None],
        al_comenzar: Callable[[], None],
        al_volver: Callable[[], None],
        al_pausar: Callable[[], None],
        al_nueva_simulacion: Callable[[], None],
        al_finalizar: Callable[[], None],
    ) -> None:
        super().__init__(master)
        self.configure(style="Dark.TFrame")
        self.pack(pady=30, fill=tk.X, padx=10)

        self._al_iniciar = al_iniciar
        self._al_comenzar = al_comenzar
        self._al_volver = al_volver
        self._al_pausar = al_pausar
        self._al_nueva_simulacion = al_nueva_simulacion
        self._al_finalizar = al_finalizar

        self.btn_principal = ttk.Button(self, command=lambda: None)
        self.btn_secundario = ttk.Button(self, command=lambda: None)
        self.btn_pausa = ttk.Button(self, command=lambda: None)

    def configurar_fase(self, fase: str) -> None:
        for widget in (self.btn_principal, self.btn_secundario, self.btn_pausa):
            widget.pack_forget()

        if fase == "listo":
            self.btn_principal.config(
                text="▶ INICIAR", command=self._al_iniciar,
            )
            self.btn_principal.pack(side=tk.LEFT, expand=True, padx=2, fill=tk.X)

        elif fase == "preparado":
            self.btn_principal.config(
                text="▶ COMENZAR", command=self._al_comenzar,
            )
            self.btn_principal.pack(side=tk.LEFT, expand=True, padx=2, fill=tk.X)
            self.btn_secundario.config(
                text="↻ VOLVER", command=self._al_volver,
            )
            self.btn_secundario.pack(side=tk.LEFT, expand=True, padx=2, fill=tk.X)

        elif fase == "ejecutando":
            self.btn_pausa.config(
                text="⏸ PAUSAR", command=self._alternar_pausa,
            )
            self.btn_pausa.pack(expand=True, padx=2, fill=tk.X)

        elif fase == "terminado":
            self.btn_principal.config(
                text="↻ NUEVA SIMULACIÓN", command=self._al_nueva_simulacion,
            )
            self.btn_principal.pack(expand=True, padx=2, fill=tk.X)

    def configurar_texto_pausa(self, pausado: bool) -> None:
        if pausado:
            self.btn_pausa.config(text="▶ REANUDAR")
            self.btn_secundario.config(
                text="⏹ FINALIZAR", command=self._al_finalizar,
            )
            self.btn_secundario.pack(side=tk.LEFT, expand=True, padx=2, fill=tk.X)
        else:
            self.btn_pausa.config(text="⏸ PAUSAR")
            self.btn_secundario.pack_forget()

    def _alternar_pausa(self) -> None:
        self._al_pausar()
