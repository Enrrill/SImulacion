import tkinter as tk
from tkinter import ttk
import csv
import os

BG_DARK = "#1E272E"
BG_PANEL = "#2F3640"
TEXT_COLOR = "#F5F6FA"
COLORS = {
    "Sanos": "#00A8FF",   
    "Inmunes": "#2ED573", 
    "Muertos": "#747D8C"  
}

class AnalyticsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analíticas de Simulaciones")
        self.root.geometry("950x650")
        self.root.configure(bg=BG_DARK)
        
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TFrame", background=BG_DARK)
        style.configure("TLabel", background=BG_DARK, foreground=TEXT_COLOR, font=("Segoe UI", 12))
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), padding=10)
        
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.main_frame, text="Promedios de Supervivencia por Configuración (Agrupado por parámetros)", style="Title.TLabel").pack(anchor="w")
        
        self.canvas = tk.Canvas(self.main_frame, bg="#11151C", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Button(self.main_frame, text="↻ Actualizar Datos", command=self.load_data).pack(pady=10)
        
        self.load_data()

    def load_data(self):
        self.canvas.delete("all")
        if not os.path.isfile("resultados.csv"):
            self.canvas.create_text(475, 250, text="No hay simulaciones registradas.\nCorre una simulación hasta el final (hasta que salga el letrero) primero.", fill="white", font=("Segoe UI", 14), justify="center")
            return
            
        groups = {}
        with open("resultados.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    pob = float(row["Poblacion"])
                    if pob == 0: continue
                    enfermedad = row.get("Enfermedad", "Personalizada")
                    if enfermedad == "Personalizada":
                        key = f"Personalizada\n(R:{row['Radio']} I:{row['Prob_Inf']})"
                    else:
                        key = enfermedad
                    
                    p_sanos = (float(row["Sanos"]) / pob) * 100
                    p_inmunes = (float(row["Inmunes"]) / pob) * 100
                    p_muertos = (float(row["Muertos"]) / pob) * 100
                    
                    if key not in groups:
                        groups[key] = []
                    groups[key].append({"Sanos": p_sanos, "Inmunes": p_inmunes, "Muertos": p_muertos, "Dias": float(row["Dias"])})
                except Exception as e:
                    continue
        
        self.draw_chart(groups)

    def draw_chart(self, groups):
        if not groups:
            self.canvas.create_text(475, 250, text="No se encontraron datos válidos.", fill="white", font=("Segoe UI", 14))
            return
            
        self.root.update_idletasks()
        c_width = self.canvas.winfo_width() or 900
        c_height = self.canvas.winfo_height() or 500
        
        num_groups = len(groups)
        max_bar_width = 40
        group_spacing = min(150, (c_width - 150) / num_groups)
        bar_width = min(max_bar_width, group_spacing / 4)
        

        self.canvas.create_line(60, c_height-70, c_width-20, c_height-70, fill="white", width=2)
        self.canvas.create_line(60, 20, 60, c_height-70, fill="white", width=2)
        
        for i in range(0, 101, 20):
            y = c_height - 70 - (i / 100) * (c_height - 100)
            self.canvas.create_line(55, y, 65, y, fill="white", width=2)
            self.canvas.create_text(40, y, text=f"{i}%", fill="white", font=("Segoe UI", 10))
            
        x_start = 60 + group_spacing / 2
        
        for i, (key, sims) in enumerate(groups.items()):
            avg_sanos = sum(s["Sanos"] for s in sims) / len(sims)
            avg_inmunes = sum(s["Inmunes"] for s in sims) / len(sims)
            avg_muertos = sum(s["Muertos"] for s in sims) / len(sims)
            
            x_center = x_start + i * group_spacing
            
            for j, (name, val) in enumerate([("Sanos", avg_sanos), ("Inmunes", avg_inmunes), ("Muertos", avg_muertos)]):
                bar_h = (val / 100) * (c_height - 100)
                bx1 = x_center + (j - 1.5) * bar_width
                by1 = c_height - 70 - bar_h
                bx2 = bx1 + bar_width
                by2 = c_height - 70
                
                self.canvas.create_rectangle(bx1, by1, bx2, by2, fill=COLORS[name], outline="")
                
                if val > 3: 
                    self.canvas.create_text((bx1+bx2)/2, by1 - 10, text=f"{val:.1f}%", fill="white", font=("Segoe UI", 9))
            
            label_text = f"{key}\n(Sims: {len(sims)})"
            self.canvas.create_text(x_center, c_height - 25, text=label_text, fill="white", font=("Segoe UI", 10, "bold"), justify="center")

        leg_x = c_width - 150
        for i, name in enumerate(["Sanos", "Inmunes", "Muertos"]):
            self.canvas.create_rectangle(leg_x, 20 + i*30, leg_x+15, 35 + i*30, fill=COLORS[name])
            self.canvas.create_text(leg_x+25, 28 + i*30, text=name, fill="white", anchor="w", font=("Segoe UI", 10, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    app = AnalyticsApp(root)
    root.mainloop()
