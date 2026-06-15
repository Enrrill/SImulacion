import csv
from pathlib import Path
from typing import Any

from src.configuracion import Estado, ConfigSimulacion


RUTA_RESULTADOS = Path("resultados.csv")

CAMPOS = [
    "Enfermedad", "Poblacion", "Radio", "Prob_Inf", "Prob_Inm",
    "Tiempo_Muerte", "Sanos", "Infectados", "Inmunes", "Muertos", "Dias",
]


def guardar_resultado(
    ruta: Path,
    enfermedad: str,
    config: ConfigSimulacion,
    estadisticas: dict[Estado, int],
    dias: int,
) -> None:
    try:
        archivo_existe = ruta.is_file()
        with ruta.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not archivo_existe:
                writer.writerow(CAMPOS)
            writer.writerow([
                enfermedad,
                config.num_individuos,
                config.radio_infeccion,
                f"{config.prob_infeccion:.4f}",
                f"{config.prob_inmunidad:.4f}",
                config.tiempo_muerte,
                estadisticas[Estado.SANO],
                estadisticas[Estado.INFECTADO],
                estadisticas[Estado.INMUNE],
                estadisticas[Estado.MUERTO],
                dias,
            ])
    except (OSError, PermissionError) as e:
        print(f"Error al guardar resultados: {e}")


def cargar_resultados(ruta: Path) -> list[dict[str, Any]]:
    if not ruta.is_file():
        return []
    try:
        with ruta.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]
    except (csv.Error, OSError, PermissionError) as e:
        print(f"Error al leer resultados: {e}")
        return []
