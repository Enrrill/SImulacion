import tkinter as tk
from tkinter import ttk, messagebox

from src.configuracion import (
    Estado, COLORES, ConfigSimulacion, PRESETS_ENFERMEDADES,
    ANCHO_SIM, ALTO_SIM, ANCHO_GRAFICO, ALTO_GRAFICO,
    ANCHO_CONTROL, FONDO_OSCURO, FONDO_PANEL, COLOR_TEXTO, INTERVALO_GRAFICO,
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
        estilo.configure("TScale", background=FONDO_PANEL, troughcolor=FONDO_OSCURO)

    def _crear_interfaz(self) -> None:
        self.val_velocidad = tk.StringVar(value="1x")
        self.val_num_individuos = tk.IntVar(value=0)
        self.val_infectados_ini = tk.IntVar(value=0)
        self.val_inmunes_ini = tk.IntVar(value=0)
        self.val_radio_infeccion = tk.IntVar(value=0)
        self.val_prob_infeccion = tk.DoubleVar(value=0.0)
        self.val_prob_inmunidad = tk.DoubleVar(value=0.0)
        self.val_tiempo_muerte = tk.IntVar(value=0)

        marco_ppal = ttk.Frame(self.root, style="Dark.TFrame")
        marco_ppal.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        marco_izq = ttk.Frame(marco_ppal, style="Dark.TFrame")
        marco_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas_sim = tk.Canvas(
            marco_izq, width=ANCHO_SIM, height=ALTO_SIM,
            bg="#11151C", highlightthickness=2, highlightbackground="#353b48",
        )
        self.canvas_sim.pack(pady=(0, 10))

        self.texto_stats = self.canvas_sim.create_text(
            15, 15, anchor="nw", fill="white", font=("Segoe UI", 12, "bold"),
        )
        self.texto_dias = self.canvas_sim.create_text(
            ANCHO_SIM - 15, 15, anchor="ne", fill="white",
            font=("Segoe UI", 12, "bold"),
        )

        self.canvas_graf = tk.Canvas(
            marco_izq, width=ANCHO_GRAFICO, height=ALTO_GRAFICO,
            bg="#11151C", highlightthickness=2, highlightbackground="#353b48",
        )
        self.canvas_graf.pack()
        self.grafico = Grafico(self.canvas_graf)

        marco_ctrl = ttk.Frame(marco_ppal, width=ANCHO_CONTROL)
        marco_ctrl.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))
        marco_ctrl.pack_propagate(False)

        ttk.Label(marco_ctrl, text="PARÁMETROS", style="Title.TLabel").pack(pady=(5, 15))

        SliderEtiquetado(marco_ctrl, "Población Total", self.val_num_individuos, 0, 500, 10)
        self.slider_infectados = SliderEtiquetado(
            marco_ctrl, "Infectados Iniciales", self.val_infectados_ini, 0, 0, 1,
        )
        self.slider_inmunes = SliderEtiquetado(
            marco_ctrl, "Inmunes Iniciales", self.val_inmunes_ini, 0, 0, 1,
        )

        self.val_num_individuos.trace_add("write", self._actualizar_max_iniciales)

        frame_vel = ttk.Frame(marco_ctrl, style="Dark.TFrame")
        frame_vel.pack(fill=tk.X, padx=15, pady=8)
        ttk.Label(frame_vel, text="Velocidad:",
                  font=("Segoe UI", 10, "bold"), foreground="#718093").pack(anchor="w")
        sub = tk.Frame(frame_vel, bg=FONDO_PANEL)
        sub.pack(fill=tk.X, pady=(5, 0))
        for v in ("1x", "1.5x", "2x"):
            tk.Radiobutton(sub, text=v, variable=self.val_velocidad, value=v,
                           bg=FONDO_PANEL, fg=COLOR_TEXTO, selectcolor="#353b48",
                           activebackground=FONDO_PANEL, activeforeground=COLOR_TEXTO,
                           bd=0, highlightthickness=0,
                           font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, expand=True)

        SliderEtiquetado(marco_ctrl, "Radio de Infección", self.val_radio_infeccion, 0, 100, 1)
        SliderEtiquetado(marco_ctrl, "Prob. de Infección", self.val_prob_infeccion, 0.0, 1.0, 0.01, formato="porcentaje")
        SliderEtiquetado(marco_ctrl, "Prob. de Inmunidad", self.val_prob_inmunidad, 0.0, 0.05, 0.0005, formato="porcentaje")
        SliderEtiquetado(marco_ctrl, "Tiempo de Vida (Frames)", self.val_tiempo_muerte, 0, 1200, 10)

        self.selector_enfermedad = SelectorEnfermedad(
            marco_ctrl, al_seleccionar=self._al_seleccionar_enfermedad,
        )
        self.botones = BotoneraControl(
            marco_ctrl,
            al_iniciar=self._preparar,
            al_comenzar=self._iniciar_simulacion,
            al_volver=self._mostrar_bienvenida,
            al_pausar=self._alternar_pausa,
            al_nueva_simulacion=self._mostrar_bienvenida,
            al_finalizar=self._finalizar_simulacion,
        )

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

        self.canvas_sim.create_text(
            ANCHO_SIM // 2, ALTO_SIM // 2,
            text="SIMULACIÓN DE EPIDEMIA\n\n"
                 "Ajusta los parámetros en el panel derecho\n"
                 "y presiona INICIAR para comenzar",
            fill="#718093", font=("Segoe UI", 16, "bold"),
            justify=tk.CENTER, tags="welcome",
        )
        self.canvas_sim.create_text(
            ANCHO_SIM // 2, ALTO_SIM - 20,
            text="Día: 0",
            fill="#718093", font=("Segoe UI", 12, "bold"), tags="welcome",
        )
        self.canvas_sim.itemconfig(self.texto_stats, text="")

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
        texto = (
            "╔══ POBLACIÓN INICIAL (Día 0) ══╗\n\n"
            f"  Sanos:      {inicial[Estado.SANO]}\n"
            f"  Infectados: {inicial[Estado.INFECTADO]}\n"
            f"  Inmunes:    {inicial[Estado.INMUNE]}\n"
            f"  Muertos:    {inicial[Estado.MUERTO]}\n\n"
            "Presiona COMENZAR para iniciar la simulación"
        )

        self.canvas_sim.create_rectangle(
            0, 0, ANCHO_SIM, ALTO_SIM,
            fill="#11151C", stipple="gray25", tags="overlay",
        )
        self.canvas_sim.create_text(
            ANCHO_SIM // 2, ALTO_SIM // 2,
            text=texto, fill="white",
            font=("Segoe UI", 14, "bold"), justify=tk.CENTER, tags="overlay",
        )
        self.canvas_sim.itemconfig(self.texto_stats, text="")
        self.canvas_sim.itemconfig(self.texto_dias, text="Día: 0")

        self.fase = "preparado"
        self.botones.configurar_fase("preparado")

    def _iniciar_simulacion(self) -> None:
        self.canvas_sim.delete("overlay")
        self.fase = "ejecutando"
        self.pausado = False
        self.botones.configurar_fase("ejecutando")
        self._bucle_principal()

    def _bucle_principal(self) -> None:
        config = self._construir_config()

        mapa_vel = {"1x": (33, 1), "1.5x": (22, 1), "2x": (16, 1)}
        demora, pasos = mapa_vel.get(self.val_velocidad.get(), (33, 1))

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
        self.canvas_sim.itemconfig(self.texto_dias, text=f"Días: {dias}")

        stats = self.motor.obtener_estadisticas()
        texto = (
            f"Sanos: {stats[Estado.SANO]} | "
            f"Infectados: {stats[Estado.INFECTADO]} | "
            f"Inmunes: {stats[Estado.INMUNE]} | "
            f"Muertos: {stats[Estado.MUERTO]}"
        )
        self.canvas_sim.itemconfig(self.texto_stats, text=texto)

        if (
            not self.motor.ejecutando
            and not self.pausado
            and stats[Estado.INFECTADO] == 0
            and len(self.canvas_sim.find_withtag("dialog")) == 0
        ):
            self._mostrar_resultados(config, stats, dias)
            return

        if self.motor.frames_transcurridos % INTERVALO_GRAFICO == 0:
            self.grafico.actualizar(self.motor.historial, self.motor.num_individuos)

        if self.motor.ejecutando or self.pausado:
            self.root.after(demora, self._bucle_principal)

    def _mostrar_resultados(
        self, config: ConfigSimulacion,
        stats: dict[Estado, int], dias: int,
    ) -> None:
        guardar_resultado(
            RUTA_RESULTADOS,
            enfermedad=self._enfermedad_actual,
            config=config,
            estadisticas=stats,
            dias=dias,
        )

        inicial = self.motor.estado_inicial
        resumen = (
            f"FIN DE LA EPIDEMIA (Día {dias})\n\n"
            f"{'':>12} {'Inicial':>8} → {'Final':>8}\n"
            f"{'Sanos:':>12} {inicial[Estado.SANO]:>8} {stats[Estado.SANO]:>8}\n"
            f"{'Infectados:':>12} {inicial[Estado.INFECTADO]:>8} {stats[Estado.INFECTADO]:>8}\n"
            f"{'Inmunes:':>12} {inicial[Estado.INMUNE]:>8} {stats[Estado.INMUNE]:>8}\n"
            f"{'Muertos:':>12} {inicial[Estado.MUERTO]:>8} {stats[Estado.MUERTO]:>8}"
        )

        cx, cy = ANCHO_SIM // 2, ALTO_SIM // 2
        self.canvas_sim.create_rectangle(
            cx - 180, cy - 110, cx + 180, cy + 110,
            fill="#2F3640", outline="#192A56", width=4, tags="dialog",
        )
        self.canvas_sim.create_text(
            cx, cy, text=resumen, fill="#F5F6FA",
            font=("Segoe UI", 13, "bold"),
            justify=tk.CENTER, tags="dialog",
        )
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
        self._mostrar_resultados(self._construir_config(), stats, dias)

    def cerrar(self) -> None:
        self.motor.ejecutando = False
        self.root.destroy()
