import tkinter as tk
from tkinter import ttk, messagebox

from src.configuracion import (
    Estado, COLORES, ConfigSimulacion, PRESETS_ENFERMEDADES,
    ANCHO_SIM, ALTO_SIM, ANCHO_GRAFICO, ALTO_GRAFICO,
    ANCHO_CONTROL, ALTO_BARRA, FONDO_OSCURO, FONDO_PANEL, COLOR_TEXTO,
    INTERVALO_GRAFICO, COLOR_SLIDER_TROUGH, COLOR_COMBOBOX_BG, COLOR_CARD_BG,
)
from src.simulacion.motor import MotorSimulacion
from src.interfaz.componentes import SliderEtiquetado, SelectorEnfermedad, BotoneraControl
from src.interfaz.grafico import Grafico
from src.almacenamiento.manejador_csv import guardar_resultado, RUTA_RESULTADOS


class Aplicacion:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Simulación de Epidemia")
        self.root.configure(bg=FONDO_OSCURO)
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)

        self.motor = MotorSimulacion()
        self.particulas_ids: list[int] = []
        self.pausado = False
        self._enfermedad_actual = "Personalizada"
        self.fase = "listo"

        self._configurar_estilo()
        self._crear_interfaz()
        self._mostrar_bienvenida()

    def _configurar_estilo(self) -> None:
        estilo = ttk.Style()
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("TFrame", background=FONDO_PANEL)
        estilo.configure("Dark.TFrame", background=FONDO_OSCURO)
        estilo.configure("TLabel", background=FONDO_PANEL, foreground=COLOR_TEXTO, font=("Segoe UI", 10))
        estilo.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), padding=10)
        estilo.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        estilo.map("TButton", background=[("active", "#4CD137")])
        estilo.configure("TScale", background=FONDO_PANEL, troughcolor=COLOR_SLIDER_TROUGH)
        estilo.configure("Card.TFrame", background=COLOR_CARD_BG)
        estilo.configure("Vertical.TScrollbar",
                         background=COLOR_SLIDER_TROUGH,
                         troughcolor=FONDO_OSCURO,
                         bordercolor=FONDO_OSCURO,
                         arrowcolor=COLOR_TEXTO)
        estilo.configure("Header.TFrame", background=FONDO_PANEL)
        estilo.configure("HeaderLabel.TLabel",
                         background=FONDO_PANEL, foreground=COLOR_TEXTO,
                         font=("Segoe UI", 11, "bold"))
        estilo.configure("Dia.TLabel",
                         background="#2F3640", foreground=COLOR_TEXTO,
                         font=("Segoe UI", 11, "bold"), padding=(10, 4))

    def _crear_barra_estado(self, master: tk.Widget) -> None:
        self._barra = ttk.Frame(master, style="Header.TFrame", height=ALTO_BARRA)
        self._barra.pack(fill=tk.X, pady=(0, 5))
        self._barra.pack_propagate(False)

        self._header_labels: dict[str, tk.Label] = {}
        self._label_dia = tk.Label(
            self._barra, text="⏱ DÍA: 0",
            bg="#2F3640", fg=COLOR_TEXTO,
            font=("Segoe UI", 11, "bold"), padx=10, pady=2,
        )
        self._label_dia.pack(side=tk.RIGHT, padx=(0, 10))

        for estado, texto in [(Estado.SANO, "SANOS"), (Estado.INFECTADO, "INFECTADOS"),
                              (Estado.INMUNE, "INMUNES"), (Estado.MUERTO, "MUERTOS")]:
            frame = tk.Frame(self._barra, bg=FONDO_PANEL)
            frame.pack(side=tk.LEFT, padx=(15, 0))
            circulo = tk.Label(frame, text="●", fg=COLORES[estado],
                               bg=FONDO_PANEL, font=("Segoe UI", 14))
            circulo.pack(side=tk.LEFT)
            lbl = tk.Label(frame, text=f"{texto}: 0",
                           bg=FONDO_PANEL, fg=COLOR_TEXTO,
                           font=("Segoe UI", 11, "bold"))
            lbl.pack(side=tk.LEFT, padx=(4, 0))
            self._header_labels[estado] = lbl

    def _crear_interfaz(self) -> None:
        self.val_velocidad = tk.DoubleVar(value=1.0)
        self.val_num_individuos = tk.IntVar(value=0)
        self.val_infectados_ini = tk.IntVar(value=0)
        self.val_inmunes_ini = tk.IntVar(value=0)
        self.val_radio_infeccion = tk.IntVar(value=0)
        self.val_prob_infeccion = tk.DoubleVar(value=0.0)
        self.val_prob_inmunidad = tk.DoubleVar(value=0.0)
        self.val_tiempo_muerte = tk.IntVar(value=0)
        self.val_max_dias = tk.IntVar(value=0)

        marco_ppal = ttk.Frame(self.root, style="Dark.TFrame")
        marco_ppal.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        marco_izq = ttk.Frame(marco_ppal, style="Dark.TFrame")
        marco_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._crear_barra_estado(marco_izq)

        self.canvas_sim = tk.Canvas(
            marco_izq, width=ANCHO_SIM, height=ALTO_SIM,
            bg="#11151C", highlightthickness=2, highlightbackground="#353b48",
        )
        self.canvas_sim.pack(pady=(0, 10))

        self.canvas_graf = tk.Canvas(
            marco_izq, width=ANCHO_GRAFICO, height=ALTO_GRAFICO,
            bg="#11151C", highlightthickness=2, highlightbackground="#353b48",
        )
        self.canvas_graf.pack()
        self.grafico = Grafico(self.canvas_graf)

        ANCHO_SCROLLBAR = 16
        self._marco_scroll = ttk.Frame(marco_ppal, width=ANCHO_CONTROL, style="Dark.TFrame")
        self._marco_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))
        self._marco_scroll.pack_propagate(False)

        self._scroll_canvas = tk.Canvas(
            self._marco_scroll, width=ANCHO_CONTROL - ANCHO_SCROLLBAR,
            bg=FONDO_OSCURO, highlightthickness=0,
        )
        self._scrollbar = ttk.Scrollbar(
            self._marco_scroll, orient="vertical", command=self._scroll_canvas.yview,
        )
        self._scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._marco_ctrl = ttk.Frame(self._scroll_canvas, style="Dark.TFrame")
        self._marco_ctrl.bind(
            "<Configure>",
            lambda e: self._scroll_canvas.configure(
                scrollregion=self._scroll_canvas.bbox("all"),
            ),
        )
        self._scroll_canvas.create_window(
            (0, 0), window=self._marco_ctrl, anchor="nw",
            width=ANCHO_CONTROL - ANCHO_SCROLLBAR,
        )
        self._scroll_canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scroll_canvas.bind("<Configure>", lambda e: self._ajustar_scroll())

        card_params = ttk.Frame(self._marco_ctrl, style="Card.TFrame")
        card_params.pack(fill=tk.X, padx=5, pady=(0, 8))

        ttk.Label(card_params, text="PARÁMETROS", style="Title.TLabel").pack(pady=(5, 5))
        ttk.Label(
            card_params, text="CONFIGURACIÓN DE SIMULACIÓN",
            font=("Segoe UI", 9), foreground="#57606F",
        ).pack(pady=(0, 5))

        SliderEtiquetado(
            card_params, "Población Total", self.val_num_individuos, 0, 500, 10,
            descripcion="Define el número de individuos presentes en el entorno.",
        )
        self.slider_infectados = SliderEtiquetado(
            card_params, "Infectados Iniciales", self.val_infectados_ini, 0, 0, 1,
        )
        self.slider_inmunes = SliderEtiquetado(
            card_params, "Inmunes Iniciales", self.val_inmunes_ini, 0, 0, 1,
        )

        self.val_num_individuos.trace_add("write", self._actualizar_max_iniciales)

        SliderEtiquetado(
            card_params, "Velocidad de Simulación", self.val_velocidad,
            0.5, 3.0, 0.1, formato="velocidad",
            descripcion="Ajusta la rapidez con la que transcurre el tiempo y el movimiento.",
        )

        SliderEtiquetado(
            card_params, "Radio de Infección", self.val_radio_infeccion, 0, 100, 1,
            descripcion="Distancia máxima a la que un infectado puede contagiar a otros.",
        )
        SliderEtiquetado(
            card_params, "Prob. de Infección", self.val_prob_infeccion, 0.0, 1.0, 0.01,
            formato="porcentaje",
            descripcion="Probabilidad de que el virus se transmita en cada contacto.",
        )
        SliderEtiquetado(
            card_params, "Prob. de Inmunidad", self.val_prob_inmunidad, 0.0, 0.05, 0.0005,
            formato="porcentaje",
            descripcion="Probabilidad de que un individuo se recupere y se vuelva inmune.",
        )
        SliderEtiquetado(
            card_params, "Tiempo de Vida (Frames)", self.val_tiempo_muerte, 0, 1200, 10,
            descripcion="Duración de la infección antes de que el individuo muera o se recupere.",
        )
        SliderEtiquetado(
            card_params, "Días Máximo", self.val_max_dias, 0, 500, 1,
            descripcion="Límite de duración de la simulación en días. 0 = sin límite.",
        )

        ttk.Separator(self._marco_ctrl, orient="horizontal").pack(fill=tk.X, padx=10, pady=4)

        card_act = ttk.Frame(self._marco_ctrl, style="Card.TFrame")
        card_act.pack(fill=tk.X, padx=5, pady=(0, 8))

        self.selector_enfermedad = SelectorEnfermedad(
            card_act, al_seleccionar=self._al_seleccionar_enfermedad,
            titulo="SELECCIONAR ENFERMEDAD",
        )
        self.botones = BotoneraControl(
            card_act,
            al_iniciar=self._preparar,
            al_comenzar=self._iniciar_simulacion,
            al_volver=self._mostrar_bienvenida,
            al_pausar=self._alternar_pausa,
            al_nueva_simulacion=self._mostrar_bienvenida,
            al_finalizar=self._finalizar_simulacion,
        )

        self.root.after_idle(self._ajustar_scroll)

    def _on_mousewheel(self, event: tk.Event) -> None:
        if event.num == 4:
            self._scroll_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._scroll_canvas.yview_scroll(1, "units")
        else:
            self._scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _ajustar_scroll(self) -> None:
        self.root.update_idletasks()
        contenido = self._marco_ctrl.winfo_reqheight()
        visible = self._scroll_canvas.winfo_height()
        if contenido <= visible:
            self._scrollbar.pack_forget()
            self._scroll_canvas.unbind("<MouseWheel>")
            self._scroll_canvas.unbind("<Button-4>")
            self._scroll_canvas.unbind("<Button-5>")
        else:
            self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self._scroll_canvas.bind("<MouseWheel>", self._on_mousewheel)
            self._scroll_canvas.bind("<Button-4>", self._on_mousewheel)
            self._scroll_canvas.bind("<Button-5>", self._on_mousewheel)

    def _construir_config(self) -> ConfigSimulacion:
        return ConfigSimulacion(
            num_individuos=self.val_num_individuos.get(),
            num_infectados_iniciales=self.val_infectados_ini.get(),
            num_inmunes_iniciales=self.val_inmunes_ini.get(),
            radio_infeccion=self.val_radio_infeccion.get(),
            prob_infeccion=self.val_prob_infeccion.get(),
            prob_inmunidad=self.val_prob_inmunidad.get(),
            tiempo_muerte=self.val_tiempo_muerte.get(),
            fps=60,
            max_dias=self.val_max_dias.get(),
        )

    def _actualizar_max_iniciales(self, *_):
        max_ = self.val_num_individuos.get()
        self.slider_infectados.configurar_rango(max_)
        self.slider_inmunes.configurar_rango(max_)

    def _al_seleccionar_enfermedad(self) -> None:
        nombre = self.selector_enfermedad.combo.get()
        if nombre == "Personalizada":
            self._enfermedad_actual = nombre
            return
        cfg = PRESETS_ENFERMEDADES.get(nombre)
        if cfg is None:
            return
        self._enfermedad_actual = nombre
        self.val_radio_infeccion.set(cfg.radio_infeccion)
        self.val_prob_infeccion.set(cfg.prob_infeccion)
        self.val_prob_inmunidad.set(cfg.prob_inmunidad)
        self.val_tiempo_muerte.set(cfg.tiempo_muerte)
        self._mostrar_bienvenida()

    def _mostrar_bienvenida(self) -> None:
        self.fase = "listo"
        self.pausado = False
        self.motor.ejecutando = False
        self.canvas_sim.delete("particle", "overlay", "dialog", "welcome")
        self.grafico.limpiar()
        self.particulas_ids = []
        self._actualizar_header(
            {Estado.SANO: 0, Estado.INFECTADO: 0,
             Estado.INMUNE: 0, Estado.MUERTO: 0},
            0,
        )

        self.canvas_sim.create_text(
            ANCHO_SIM // 2, ALTO_SIM // 2,
            text="SIMULACIÓN DE EPIDEMIA\n\n"
                 "Ajusta los parámetros en el panel derecho\n"
                 "y presiona INICIAR para comenzar",
            fill="#718093", font=("Segoe UI", 16, "bold"),
            justify=tk.CENTER, tags="welcome",
        )

        self.botones.configurar_fase("listo")

    def _preparar(self) -> None:
        errores: list[str] = []
        if self.val_num_individuos.get() == 0:
            errores.append("Población Total")
        if self.val_infectados_ini.get() == 0:
            errores.append("Infectados Iniciales")
        if self.val_radio_infeccion.get() == 0:
            errores.append("Radio de Infección")
        if self.val_prob_infeccion.get() == 0.0:
            errores.append("Prob. de Infección")
        if self.val_tiempo_muerte.get() == 0:
            errores.append("Tiempo de Vida (Frames)")
        if errores:
            messagebox.showwarning(
                "Parámetros sin ajustar",
                "Los siguientes parámetros están en 0:\n\n"
                + "\n".join(f"  • {e}" for e in errores)
                + "\n\nAjústalos antes de iniciar.",
            )
            return

        n_ind = self.val_num_individuos.get()
        if self.val_infectados_ini.get() + self.val_inmunes_ini.get() > n_ind:
            messagebox.showwarning(
                "Población excedida",
                "La suma de Infectados e Inmunes iniciales "
                f"({self.val_infectados_ini.get()} + {self.val_inmunes_ini.get()} = "
                f"{self.val_infectados_ini.get() + self.val_inmunes_ini.get()}) "
                f"supera la población total ({n_ind}).\n\n"
                "Reduce la cantidad de Infectados o Inmunes iniciales.",
            )
            return

        config = self._construir_config()
        self.motor.reiniciar(config)

        self.canvas_sim.delete("particle", "overlay", "dialog", "welcome")
        self.particulas_ids = []

        for ind in self.motor.poblacion:
            pid = self.canvas_sim.create_oval(
                ind.x - ind.radio, ind.y - ind.radio,
                ind.x + ind.radio, ind.y + ind.radio,
                fill=COLORES[ind.estado], outline="", tags="particle",
            )
            self.particulas_ids.append(pid)

        inicial = self.motor.estado_inicial
        cx, cy = ANCHO_SIM // 2, ALTO_SIM // 2

        # overlay oscuro de fondo
        self.canvas_sim.create_rectangle(
            0, 0, ANCHO_SIM, ALTO_SIM,
            fill="#11151C", stipple="gray25", tags="overlay",
        )
        # sombra de la tarjeta
        self.canvas_sim.create_rectangle(
            cx - 190, cy - 145, cx + 190, cy + 145,
            fill="#0D1117", outline="", tags="overlay",
        )
        # tarjeta principal
        self.canvas_sim.create_rectangle(
            cx - 185, cy - 140, cx + 185, cy + 140,
            fill="#252C34", outline="#4B7BEC", width=2, tags="overlay",
        )
        # título
        self.canvas_sim.create_text(
            cx, cy - 115, text="📊 POBLACIÓN INICIAL (Día 0)",
            fill="#F5F6FA", font=("Segoe UI", 14, "bold"),
            justify=tk.CENTER, tags="overlay",
        )
        # línea separadora
        self.canvas_sim.create_line(
            cx - 155, cy - 85, cx + 155, cy - 85,
            fill="#4B7BEC", width=1, tags="overlay",
        )
        # encabezado de tabla
        self.canvas_sim.create_text(
            cx - 90, cy - 50, text="Estado", fill="#718093",
            font=("Segoe UI", 10, "bold"), anchor="w", tags="overlay",
        )
        self.canvas_sim.create_text(
            cx + 90, cy - 50, text="Inicial", fill="#718093",
            font=("Segoe UI", 10, "bold"), anchor="e", tags="overlay",
        )
        # estados
        y = cy - 25
        for estado, icono in [(Estado.SANO, "🟦"), (Estado.INFECTADO, "🟥"),
                               (Estado.INMUNE, "🟩"), (Estado.MUERTO, "⬜")]:
            self.canvas_sim.create_text(
                cx - 90, y, text=f"{icono} {estado.name}", fill=COLORES[estado],
                font=("Segoe UI", 12, "bold"), anchor="w", tags="overlay",
            )
            self.canvas_sim.create_text(
                cx + 90, y, text=str(inicial[estado]), fill=COLOR_TEXTO,
                font=("Segoe UI", 12, "bold"), anchor="e", tags="overlay",
            )
            y += 26
        # prompt
        self.canvas_sim.create_text(
            cx, cy + 105, text="Presiona COMENZAR para iniciar la simulación",
            fill="#718093", font=("Segoe UI", 11, "bold"),
            justify=tk.CENTER, tags="overlay",
        )
        self._actualizar_header(inicial, 0)

        self.fase = "preparado"
        self.botones.configurar_fase("preparado")

    def _iniciar_simulacion(self) -> None:
        self.canvas_sim.delete("overlay")
        self.fase = "ejecutando"
        self.pausado = False
        self.botones.configurar_fase("ejecutando")
        self._bucle_principal()

    def _actualizar_header(self, stats: dict[Estado, int], dias: int) -> None:
        for estado, conteo in stats.items():
            self._header_labels[estado].config(text=f"{estado.name}: {conteo}")
        self._label_dia.config(text=f"⏱ DÍA: {dias}")

    def _bucle_principal(self) -> None:
        config = self._construir_config()

        velocidad = self.val_velocidad.get()
        demora = max(10, int(33 / velocidad))
        pasos = 1

        if not self.pausado:
            for _ in range(pasos):
                self.motor.avanzar(config)
                if not self.motor.ejecutando:
                    break

        for i, ind in enumerate(self.motor.poblacion):
            pid = self.particulas_ids[i]
            self.canvas_sim.coords(
                pid, ind.x - ind.radio, ind.y - ind.radio,
                ind.x + ind.radio, ind.y + ind.radio,
            )
            self.canvas_sim.itemconfig(pid, fill=COLORES[ind.estado])

        dias = self.motor.frames_transcurridos // 60
        stats = self.motor.obtener_estadisticas()
        self._actualizar_header(stats, dias)

        if (
            not self.motor.ejecutando
            and not self.pausado
            and len(self.canvas_sim.find_withtag("dialog")) == 0
        ):
            motivo = "limite" if (config.max_dias > 0 and dias >= config.max_dias) else "extinguida"
            self._mostrar_resultados(config, stats, dias, motivo)
            return

        if self.motor.frames_transcurridos % INTERVALO_GRAFICO == 0:
            self.grafico.actualizar(self.motor.historial, self.motor.num_individuos)

        if self.motor.ejecutando or self.pausado:
            self.root.after(demora, self._bucle_principal)

    def _mostrar_resultados(
        self, config: ConfigSimulacion,
        stats: dict[Estado, int], dias: int,
        motivo: str = "extinguida",
    ) -> None:
        guardar_resultado(
            RUTA_RESULTADOS,
            enfermedad=self._enfermedad_actual,
            config=config,
            estadisticas=stats,
            dias=dias,
        )

        inicial = self.motor.estado_inicial

        cx, cy = ANCHO_SIM // 2, ALTO_SIM // 2
        # sombra
        self.canvas_sim.create_rectangle(
            cx - 205, cy - 130, cx + 205, cy + 130,
            fill="#0D1117", outline="", tags="dialog",
        )
        # tarjeta
        self.canvas_sim.create_rectangle(
            cx - 200, cy - 125, cx + 200, cy + 125,
            fill="#252C34", outline="#E74C3C", width=2, tags="dialog",
        )
        # título
        titulos = {
            "extinguida": f"🏁 EPIDEMIA EXTINGUIDA (Día {dias})",
            "limite": f"⏰ LÍMITE DE DÍAS ALCANZADO (Día {dias})",
            "manual": f"⏹ SIMULACIÓN FINALIZADA (Día {dias})",
        }
        self.canvas_sim.create_text(
            cx, cy - 95, text=titulos.get(motivo, titulos["extinguida"]),
            fill="#F5F6FA", font=("Segoe UI", 13, "bold"),
            justify=tk.CENTER, tags="dialog",
        )
        # línea separadora
        self.canvas_sim.create_line(
            cx - 170, cy - 70, cx + 170, cy - 70,
            fill="#E74C3C", width=1, tags="dialog",
        )
        # tabla comparativa
        y = cy - 45
        self.canvas_sim.create_text(
            cx - 100, y, text="Estado", fill="#718093",
            font=("Segoe UI", 10, "bold"), anchor="w", tags="dialog",
        )
        self.canvas_sim.create_text(
            cx + 40, y, text="Inicial", fill="#718093",
            font=("Segoe UI", 10, "bold"), anchor="e", tags="dialog",
        )
        self.canvas_sim.create_text(
            cx + 130, y, text="Final", fill="#718093",
            font=("Segoe UI", 10, "bold"), anchor="e", tags="dialog",
        )
        y += 25
        for estado, icono in [(Estado.SANO, "🟦"), (Estado.INFECTADO, "🟥"),
                               (Estado.INMUNE, "🟩"), (Estado.MUERTO, "⬜")]:
            self.canvas_sim.create_text(
                cx - 100, y, text=f"{icono} {estado.name}", fill=COLORES[estado],
                font=("Segoe UI", 11, "bold"), anchor="w", tags="dialog",
            )
            self.canvas_sim.create_text(
                cx + 40, y, text=str(inicial[estado]), fill=COLOR_TEXTO,
                font=("Segoe UI", 11), anchor="e", tags="dialog",
            )
            self.canvas_sim.create_text(
                cx + 130, y, text=str(stats[estado]), fill=COLOR_TEXTO,
                font=("Segoe UI", 11, "bold"), anchor="e", tags="dialog",
            )
            y += 26
        self.grafico.actualizar(self.motor.historial, self.motor.num_individuos)

        self.fase = "terminado"
        self.botones.configurar_fase("terminado")

    def _alternar_pausa(self) -> None:
        if not self.motor.ejecutando:
            return
        self.pausado = not self.pausado
        self.botones.configurar_texto_pausa(self.pausado)

    def _finalizar_simulacion(self) -> None:
        self.motor.ejecutando = False
        self.pausado = False
        stats = self.motor.obtener_estadisticas()
        dias = self.motor.frames_transcurridos // 60
        self._mostrar_resultados(self._construir_config(), stats, dias, "manual")

    def cerrar(self) -> None:
        self.motor.ejecutando = False
        self.root.destroy()
