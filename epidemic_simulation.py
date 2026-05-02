import tkinter as tk
from tkinter import ttk
import random
import math


SIM_WIDTH, SIM_HEIGHT = 800, 500
GRAPH_WIDTH, GRAPH_HEIGHT = 800, 150
CONTROL_WIDTH = 280

NUM_INDIVIDUALS = 150
INITIAL_INFECTED = 3

SUSCEPTIBLE = 0
INFECTED = 1
IMMUNE = 2
DEAD = 3

COLORS = {
    SUSCEPTIBLE: "#00A8FF",  
    INFECTED: "#FF4757",      
    IMMUNE: "#2ED573",        
    DEAD: "#747D8C"           
}

BG_DARK = "#1E272E"
BG_PANEL = "#2F3640"
TEXT_COLOR = "#F5F6FA"

class Individual:
    def __init__(self, x, y, state, canvas, app):
        self.x = x
        self.y = y
        self.state = state
        self.radius = 6
        self.canvas = canvas
        self.app = app
        
   
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 3.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.death_timer = 0
        self.initial_death_timer = 0
        self.reinfection_prob = 0.0
        
        self.id = canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill=COLORS[self.state], outline="", tags="particle"
        )
        
        if self.state == INFECTED:
            self.infect()

    def infect(self):
        self.state = INFECTED
        self.death_timer = self.app.val_death_timer.get()
        self.initial_death_timer = self.death_timer
        self.canvas.itemconfig(self.id, fill=COLORS[self.state])

    def move(self):
        if self.state == DEAD:
            return
            
        self.x += self.vx
        self.y += self.vy
        
        if self.x - self.radius < 0 or self.x + self.radius > SIM_WIDTH:
            self.vx *= -1
            self.x = max(self.radius, min(self.x, SIM_WIDTH - self.radius))
            
        if self.y - self.radius < 0 or self.y + self.radius > SIM_HEIGHT:
            self.vy *= -1
            self.y = max(self.radius, min(self.y, SIM_HEIGHT - self.radius))
            
        self.canvas.coords(self.id, self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius)

    def update_infection(self):
        if self.state == INFECTED:
            if random.random() < self.app.val_immunity_prob.get():
                self.state = IMMUNE
                inf_prob = self.app.val_infection_prob.get()
                self.reinfection_prob = inf_prob * (self.death_timer / max(1, self.initial_death_timer))
                self.canvas.itemconfig(self.id, fill=COLORS[self.state])
                return
                
            self.death_timer -= 1
            if self.death_timer <= 0:
                self.state = DEAD
                self.canvas.itemconfig(self.id, fill=COLORS[self.state])


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación de Epidemia")
        self.root.configure(bg=BG_DARK)
        
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
        self.val_infection_radius = tk.IntVar(value=30)
        self.val_infection_prob = tk.DoubleVar(value=0.05)
        self.val_immunity_prob = tk.DoubleVar(value=0.002)
        self.val_death_timer = tk.Int
        self.main_frame = ttk.Frame(root, style="Dark.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.left_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.sim_canvas = tk.Canvas(self.left_frame, width=SIM_WIDTH, height=SIM_HEIGHT, 
                                  bg="#11151C", highlightthickness=2, highlightbackground="#353b48")
        self.sim_canvas.pack(pady=(0, 10))
        
        self.stats_text = self.sim_canvas.create_text(15, 15, anchor="nw", fill="white", font=("Segoe UI", 12, "bold"))
        self.days_text = self.sim_canvas.create_text(SIM_WIDTH - 15, 15, anchor="ne", fill="white", font=("Segoe UI", 12, "bold"))
        
        self.graph_canvas = tk.Canvas(self.left_frame, width=GRAPH_WIDTH, height=GRAPH_HEIGHT, 
                                    bg="#11151C", highlightthickness=2, highlightbackground="#353b48")
        self.graph_canvas.pack()
        
        self.control_frame = ttk.Frame(self.main_frame, width=CONTROL_WIDTH)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))
        
        ttk.Label(self.control_frame, text="PARAMETROS", style="Title.TLabel").pack(pady=(5, 15))
        
        self.create_slider("Velocidad (FPS)", self.val_fps, 10, 120, 1)
        self.create_slider("Radio de Infección", self.val_infection_radius, 10, 100, 1)
        self.create_slider("Prob. de Infección (%)", self.val_infection_prob, 0.01, 1.0, 0.01)
        self.create_slider("Prob. de Inmunidad (%)", self.val_immunity_prob, 0.0001, 0.05, 0.0005)
        self.create_slider("Tiempo de Vida (Frames)", self.val_death_timer, 100, 1200, 10)
        
        btn_frame = ttk.Frame(self.control_frame)
        btn_frame.pack(pady=30, fill=tk.X, padx=10)
        
        self.btn_restart = ttk.Button(btn_frame, text="▶ REINICIAR", command=self.restart_simulation)
        self.btn_restart.pack(side=tk.LEFT, expand=True, padx=2, fill=tk.X)
        
        self.pause_btn = ttk.Button(btn_frame, text="⏸ PAUSAR", command=self.toggle_pause)
        self.pause_btn.pack(side=tk.RIGHT, expand=True, padx=2, fill=tk.X)
        
        self.max_history = GRAPH_WIDTH
        self.is_running = False
        self.is_paused = False
        self.restart_simulation()

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

    def toggle_pause(self):
        if not self.is_running:
            return
        self.is_paused = not self.is_paused
        self.pause_btn.config(text="▶ REANUDAR" if self.is_paused else "⏸ PAUSAR")

    def restart_simulation(self):
        self.is_paused = False
        self.pause_btn.config(text="⏸ PAUSAR")
        self.sim_canvas.delete("particle", "dialog")
        self.graph_canvas.delete("all")
        
        self.history = {SUSCEPTIBLE: [], INFECTED: [], IMMUNE: [], DEAD: []}
        self.frames_passed = 0
        
        self.population = []
        for i in range(NUM_INDIVIDUALS):
            x = random.randint(20, SIM_WIDTH - 20)
            y = random.randint(20, SIM_HEIGHT - 20)
            state = INFECTED if i < INITIAL_INFECTED else SUSCEPTIBLE
            self.population.append(Individual(x, y, state, self.sim_canvas, self))
            
        if not self.is_running:
            self.is_running = True
            self.update()

    def update(self):
        fps = max(1, self.val_fps.get())
        if not self.is_running:
            return
            
        if self.is_paused:
            self.root.after(1000 // fps, self.update)
            return
            
        self.frames_passed += 1
        dias = self.frames_passed // 60
        self.sim_canvas.itemconfig(self.days_text, text=f"Días: {dias}")

        for p in self.population:
            p.move()
            p.update_infection()
            
        infected_pop = [p for p in self.population if p.state == INFECTED]
        susceptible_pop = [p for p in self.population if p.state == SUSCEPTIBLE]
        immune_pop = [p for p in self.population if p.state == IMMUNE]
        
        radius = self.val_infection_radius.get()
        inf_prob = self.val_infection_prob.get()
        
        for inf in infected_pop:
            for sus in susceptible_pop:
                dist = math.hypot(inf.x - sus.x, inf.y - sus.y)
                if dist < radius:
                    if random.random() < inf_prob:
                        sus.infect()
                        susceptible_pop.remove(sus)
                        
            for imm in immune_pop:
                dist = math.hypot(inf.x - imm.x, inf.y - imm.y)
                if dist < radius:
                    if random.random() < imm.reinfection_prob:
                        imm.infect()
                        immune_pop.remove(imm)

        stats = {
            SUSCEPTIBLE: len(susceptible_pop),
            INFECTED: len(infected_pop),
            IMMUNE: len(immune_pop),
            DEAD: sum(1 for p in self.population if p.state == DEAD),
        }
        
        stats_str = f"Sanos: {stats[SUSCEPTIBLE]} | Infectados: {stats[INFECTED]} | Inmunes: {stats[IMMUNE]} | Muertos: {stats[DEAD]}"
        self.sim_canvas.itemconfig(self.stats_text, text=stats_str)
        
        if stats[INFECTED] == 0:
            self.is_running = False
            vivos = stats[SUSCEPTIBLE] + stats[IMMUNE]
            resumen = f"FIN DE LA EPIDEMIA (Día {self.frames_passed // 60})\n\n"
            resumen += f"Vivos: {vivos}\n"
            resumen += f"Muertos: {stats[DEAD]}\n"
            resumen += f"Inmunes: {stats[IMMUNE]}\n"
            resumen += f"Ilesos: {stats[SUSCEPTIBLE]}"
            
            cx, cy = SIM_WIDTH//2, SIM_HEIGHT//2
            self.sim_canvas.create_rectangle(cx - 150, cy - 90, cx + 150, cy + 90, fill="#2F3640", outline="#192A56", width=4, tags="dialog")
            self.sim_canvas.create_text(cx, cy, text=resumen, fill="#F5F6FA", font=("Segoe UI", 14, "bold"), justify=tk.CENTER, tags="dialog")
            
            self.draw_graph()
            return
        
        for state in self.history:
            self.history[state].append(stats[state])
            if len(self.history[state]) > self.max_history:
                self.history[state].pop(0)
                
        self.draw_graph()
        
        self.root.after(1000 // fps, self.update)

    def draw_graph(self):
        self.graph_canvas.delete("all")
        if len(self.history[SUSCEPTIBLE]) < 2: return
            
        for state in self.history:
            points = []
            for x, count in enumerate(self.history[state]):
                y = GRAPH_HEIGHT - (count / NUM_INDIVIDUALS) * GRAPH_HEIGHT
                points.append(x)
                points.append(y)
            if points:
                self.graph_canvas.create_line(*points, fill=COLORS[state], width=3, smooth=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
