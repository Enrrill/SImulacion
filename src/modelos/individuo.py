import random
import math
from dataclasses import dataclass, field

from src.configuracion import Estado, ANCHO_SIM, ALTO_SIM


@dataclass
class Individuo:
    x: float
    y: float
    estado: Estado = Estado.SANO
    radio: int = 6
    vx: float = field(init=False)
    vy: float = field(init=False)
    temporizador_muerte: int = 0
    temporizador_inicial: int = 0
    prob_reinfeccion: float = 0.0

    def __post_init__(self) -> None:
        angulo = random.uniform(0, 2 * math.pi)
        rapidez = random.uniform(1.5, 3.0)
        self.vx = math.cos(angulo) * rapidez
        self.vy = math.sin(angulo) * rapidez

    @property
    def vivo(self) -> bool:
        return self.estado != Estado.MUERTO

    @property
    def posicion(self) -> tuple[float, float]:
        return (self.x, self.y)

    def infectar(self, tiempo_muerte: int) -> None:
        self.estado = Estado.INFECTADO
        self.temporizador_muerte = tiempo_muerte
        self.temporizador_inicial = tiempo_muerte

    def mover(self, ancho: int = ANCHO_SIM, alto: int = ALTO_SIM) -> None:
        if self.estado == Estado.MUERTO:
            return

        self.x += self.vx
        self.y += self.vy

        if self.x - self.radio < 0 or self.x + self.radio > ancho:
            self.vx *= -1
            self.x = max(self.radio, min(self.x, ancho - self.radio))

        if self.y - self.radio < 0 or self.y + self.radio > alto:
            self.vy *= -1
            self.y = max(self.radio, min(self.y, alto - self.radio))

    def actualizar_infeccion(
        self, prob_inmunidad: float, prob_infeccion: float,
    ) -> bool:
        if self.estado != Estado.INFECTADO:
            return False

        if random.random() < prob_inmunidad:
            self.estado = Estado.INMUNE
            self.prob_reinfeccion = prob_infeccion * (
                self.temporizador_muerte / max(1, self.temporizador_inicial)
            )
            return True

        self.temporizador_muerte -= 1
        if self.temporizador_muerte <= 0:
            self.estado = Estado.MUERTO
            return True

        return False
