import tkinter as tk
from tkinter import ttk
import os
import csv
from config import *
from engine import Simulation

DISEASE_PRESETS = {
    "Personalizada": None,
    "COVID-19": (40, 0.20, 0.005, 1000),
    "Peste Negra": (25, 0.15, 0.001, 300),
    "Viruela": (35, 0.30, 0.003, 600),
    "Gripe Española": (50, 0.40, 0.008, 450),
    "Peste de Justiniano": (20, 0.12, 0.0015, 350),
    "Cólera": (15, 0.80, 0.006, 200)
}

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación de Epidemia")
        self.root.configure(bg=BG_DARK)
        
        # Backend Engine
        self.sim = Simulation()
        self.particle_ids = []
        self.is_paused = False
        
        self.setup_ui()
        self.restart_simulation()

    def setup_ui(self):
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
            
        style.configure("TFrame", background=BG_PANEL)
        style.configure("Dark.TFrame", background=BG_DARK)
        style.configure("TLabel", background=BG_PANEL, foreground=TEXT_COLOR, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), padding=10)
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.map("TButton", background=[("active", "#4CD137")])
        style.configure("TScale", background=BG_PANEL, troughcolor=BG_DARK)

        self.val_fps = tk.IntVar(value=60)
        self.val_num_individuals = tk.IntVar(value=NUM_INDIVIDUALS)
        self.val_infection_radius = tk.IntVar(value=30)
        self.val_infection_prob = tk.DoubleVar(value=0.05)
        self.val_immunity_prob = tk.DoubleVar(value=0.002)
        self.val_death_timer = tk.IntVar(value=450)
        
        self.main_frame = ttk.Frame(self.root, style="Dark.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.left_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.sim_canvas = tk.Canvas(self.left_frame, width=SIM_WIDTH, height=SIM_HEIGHT, bg="#11151C", highlightthickness=2, highlightbackground="#353b48")
        self.sim_canvas.pack(pady=(0, 10))
        
        self.stats_text = self.sim_canvas.create_text(15, 15, anchor="nw", fill="white", font=("Segoe UI", 12, "bold"))
        self.days_text = self.sim_canvas.create_text(SIM_WIDTH - 15, 15, anchor="ne", fill="white", font=("Segoe UI", 12, "bold"))
        
        self.graph_canvas = tk.Canvas(self.left_frame, width=GRAPH_WIDTH, height=GRAPH_HEIGHT, bg="#11151C", highlightthickness=2, highlightbackground="#353b48")
        self.graph_canvas.pack()
        
        self.control_frame = ttk.Frame(self.main_frame, width=CONTROL_WIDTH)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))
        
        ttk.Label(self.control_frame, text="PARAMETROS", style="Title.TLabel").pack(pady=(5, 15))
        
        self.create_slider("Población Total", self.val_num_individuals, 10, 500, 10)
        self.create_slider("Velocidad de Simulación", self.val_fps, 10, 300, 10)
        self.create_slider("Radio de Infección", self.val_infection_radius, 10, 100, 1)
        self.create_slider("Prob. de Infección (%)", self.val_infection_prob, 0.01, 1.0, 0.01)
        self.create_slider("Prob. de Inmunidad (%)", self.val_immunity_prob, 0.0001, 0.05, 0.0005)
        self.create_slider("Tiempo de Vida (Frames)", self.val_death_timer, 100, 1200, 10)
        
        preset_frame = ttk.Frame(self.control_frame)
        preset_frame.pack(pady=(15, 0), fill=tk.X, padx=15)
        ttk.Label(preset_frame, text="Seleccionar Enfermedad:").pack(anchor="w")
        self.combo_disease = ttk.Combobox(preset_frame, values=list(DISEASE_PRESETS.keys()), state="readonly", font=("Segoe UI", 10))
        self.combo_disease.set("Personalizada")
        self.combo_disease.pack(fill=tk.X, pady=(5,0))
        self.combo_disease.bind("<<ComboboxSelected>>", self.on_disease_selected)
        
        btn_frame = ttk.Frame(self.control_frame)
        btn_frame.pack(pady=30, fill=tk.X, padx=10)
        
        self.btn_restart = ttk.Button(btn_frame, text="▶ REINICIAR", command=self.restart_simulation)
        self.btn_restart.pack(side=tk.LEFT, expand=True, padx=2, fill=tk.X)
        
        self.pause_btn = ttk.Button(btn_frame, text="⏸ PAUSAR", command=self.toggle_pause)
        self.pause_btn.pack(side=tk.RIGHT, expand=True, padx=2, fill=tk.X)

    def create_slider(self, label_text, variable, min_val, max_val, resolution):
        frame = ttk.Frame(self.control_frame)
        frame.pack(fill=tk.X, padx=15, pady=8)
        
        label_var = tk.StringVar()
        def update_label(*args):
            val = variable.get()
            if isinstance(val, float):
                label_var.set(f"{label_text}: {val:.4f}")
            else:
                label_var.set(f"{label_text}: {val}")
        variable.trace_add("write", update_label)
        update_label()
        
        ttk.Label(frame, textvariable=label_var, font=("Segoe UI", 10, "bold"), foreground="#718093").pack(anchor="w")
        ttk.Scale(frame, variable=variable, from_=min_val, to=max_val, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(5,0))

    def on_disease_selected(self, event=None):
        disease = self.combo_disease.get()
        if disease != "Personalizada":
            rad, inf, inm, time = DISEASE_PRESETS[disease]
            self.val_infection_radius.set(rad)
            self.val_infection_prob.set(inf)
            self.val_immunity_prob.set(inm)
            self.val_death_timer.set(time)
        self.restart_simulation()

    def toggle_pause(self):
        if not self.sim.is_running: return
        self.is_paused = not self.is_paused
        self.pause_btn.config(text="▶ REANUDAR" if self.is_paused else "⏸ PAUSAR")

    def init_particles(self):
        self.sim_canvas.delete("particle")
        self.particle_ids = []
        for p in self.sim.population:
            pid = self.sim_canvas.create_oval(
                p.x - p.radius, p.y - p.radius,
                p.x + p.radius, p.y + p.radius,
                fill=COLORS[p.state], outline="", tags="particle"
            )
            self.particle_ids.append(pid)

    def restart_simulation(self):
        self.is_paused = False
        self.pause_btn.config(text="⏸ PAUSAR")
        self.sim_canvas.delete("dialog")
        
        self.sim.restart(self.val_num_individuals.get())
        
        # Asignar tiempo de muerte inicial a los infectados
        for p in self.sim.population:
            if p.state == INFECTED:
                p.infect(self.val_death_timer.get())

        self.init_particles()
        
        self.update()

    def update(self):
        velocidad = max(1, self.val_fps.get())
        
        steps = 1
        delay = 1000 // velocidad
        
        # Windows Tkinter no puede dibujar a más de ~64 FPS (16ms)
        # Si se pide más velocidad, calculamos más turnos lógicos por fotograma
        if velocidad > 60:
            delay = 16
            steps = velocidad // 60
            
        # --- Lógica delegada al Backend ---
        for _ in range(steps):
            stats = self.sim.step(
                radius=self.val_infection_radius.get(),
                inf_prob=self.val_infection_prob.get(),
                immunity_prob=self.val_immunity_prob.get(),
                death_timer_val=self.val_death_timer.get(),
                is_paused=self.is_paused
            )
            if not self.sim.is_running:
                break
        
        # --- Actualización del Frontend ---
        for i, p in enumerate(self.sim.population):
            pid = self.particle_ids[i]
            self.sim_canvas.coords(pid, p.x - p.radius, p.y - p.radius, p.x + p.radius, p.y + p.radius)
            self.sim_canvas.itemconfig(pid, fill=COLORS[p.state])
            
        dias = self.sim.frames_passed // 60
        self.sim_canvas.itemconfig(self.days_text, text=f"Días: {dias}")
        
        stats_str = f"Sanos: {stats[SUSCEPTIBLE]} | Infectados: {stats[INFECTED]} | Inmunes: {stats[IMMUNE]} | Muertos: {stats[DEAD]}"
        self.sim_canvas.itemconfig(self.stats_text, text=stats_str)
        
        if not self.sim.is_running and not self.is_paused and stats[INFECTED] == 0 and len(self.sim_canvas.find_withtag("dialog")) == 0:
            vivos = stats[SUSCEPTIBLE] + stats[IMMUNE]
            resumen = f"FIN DE LA EPIDEMIA (Día {dias})\n\n"
            resumen += f"Vivos: {vivos}\n"
            resumen += f"Muertos: {stats[DEAD]}\n"
            resumen += f"Inmunes: {stats[IMMUNE]}\n"
            resumen += f"Ilesos: {stats[SUSCEPTIBLE]}"
            
            self.save_results(stats, dias)
            
            cx, cy = SIM_WIDTH//2, SIM_HEIGHT//2
            self.sim_canvas.create_rectangle(cx - 150, cy - 90, cx + 150, cy + 90, fill="#2F3640", outline="#192A56", width=4, tags="dialog")
            self.sim_canvas.create_text(cx, cy, text=resumen, fill="#F5F6FA", font=("Segoe UI", 14, "bold"), justify=tk.CENTER, tags="dialog")
            self.draw_graph()
            self.draw_graph()
            return
            
        if self.sim.frames_passed % 5 == 0:
            self.draw_graph()
        
        # Siguiente frame si sigue corriendo
        if self.sim.is_running or self.is_paused:
            self.root.after(delay, self.update)

    def save_results(self, stats, dias):
        file_exists = os.path.isfile("resultados.csv")
        with open("resultados.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Enfermedad", "Poblacion", "Radio", "Prob_Inf", "Prob_Inm", "Tiempo_Muerte", "Sanos", "Infectados", "Inmunes", "Muertos", "Dias"])
            
            pob = self.val_num_individuals.get()
            writer.writerow([
                self.combo_disease.get(),
                pob,
                self.val_infection_radius.get(),
                f"{self.val_infection_prob.get():.4f}",
                f"{self.val_immunity_prob.get():.4f}",
                self.val_death_timer.get(),
                stats[SUSCEPTIBLE],
                stats[INFECTED],
                stats[IMMUNE],
                stats[DEAD],
                dias
            ])

    def draw_graph(self):
        self.graph_canvas.delete("all")
        if len(self.sim.history[SUSCEPTIBLE]) < 2: return
            
        for state in self.sim.history:
            points = []
            for x, count in enumerate(self.sim.history[state]):
                y = GRAPH_HEIGHT - (count / self.sim.num_individuals) * GRAPH_HEIGHT
                points.append(x)
                points.append(y)
            if points:
                self.graph_canvas.create_line(*points, fill=COLORS[state], width=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
