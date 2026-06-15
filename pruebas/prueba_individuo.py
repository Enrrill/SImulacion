import pytest
from src.configuracion import Estado, ANCHO_SIM, ALTO_SIM
from src.modelos.individuo import Individuo


class TestIndividuo:
    def test_creacion_valores_iniciales(self) -> None:
        ind = Individuo(x=100.0, y=200.0, estado=Estado.SANO)
        assert ind.x == 100.0
        assert ind.y == 200.0
        assert ind.estado == Estado.SANO
        assert ind.radio == 6
        assert ind.temporizador_muerte == 0
        assert ind.vivo

    def test_infectar_cambia_estado(self) -> None:
        ind = Individuo(x=100.0, y=200.0, estado=Estado.SANO)
        ind.infectar(tiempo_muerte=450)
        assert ind.estado == Estado.INFECTADO
        assert ind.temporizador_muerte == 450
        assert ind.temporizador_inicial == 450

    def test_mover_muerto_no_se_mueve(self) -> None:
        ind = Individuo(x=100.0, y=200.0, estado=Estado.MUERTO)
        x_ant, y_ant = ind.x, ind.y
        ind.mover()
        assert ind.x == x_ant
        assert ind.y == y_ant

    def test_mover_cambia_posicion(self) -> None:
        ind = Individuo(x=400.0, y=250.0, estado=Estado.SANO)
        x_ant, y_ant = ind.x, ind.y
        ind.mover()
        assert (ind.x, ind.y) != (x_ant, y_ant)

    def test_rebote_pared_izquierda(self) -> None:
        ind = Individuo(x=5.0, y=250.0, estado=Estado.SANO)
        ind.vx = -2.0
        ind.vy = 0.0
        ind.mover()
        assert ind.x >= ind.radio
        assert ind.vx > 0

    def test_rebote_pared_derecha(self) -> None:
        ind = Individuo(x=795.0, y=250.0, estado=Estado.SANO)
        ind.vx = 2.0
        ind.vy = 0.0
        ind.mover(ancho=ANCHO_SIM)
        assert ind.x <= ANCHO_SIM - ind.radio
        assert ind.vx < 0

    def test_rebote_pared_superior(self) -> None:
        ind = Individuo(x=400.0, y=3.0, estado=Estado.SANO)
        ind.vx = 0.0
        ind.vy = -2.0
        ind.mover(alto=ALTO_SIM)
        assert ind.y >= ind.radio
        assert ind.vy > 0

    def test_rebote_pared_inferior(self) -> None:
        ind = Individuo(x=400.0, y=495.0, estado=Estado.SANO)
        ind.vx = 0.0
        ind.vy = 2.0
        ind.mover(alto=ALTO_SIM)
        assert ind.y <= ALTO_SIM - ind.radio
        assert ind.vy < 0

    def test_actualizar_infeccion_se_vuelve_inmune(self) -> None:
        ind = Individuo(x=100.0, y=200.0, estado=Estado.INFECTADO)
        ind.infectar(tiempo_muerte=450)
        cambiado = ind.actualizar_infeccion(prob_inmunidad=1.0, prob_infeccion=0.05)
        assert cambiado
        assert ind.estado == Estado.INMUNE

    def test_actualizar_infeccion_muere_por_tiempo(self) -> None:
        ind = Individuo(x=100.0, y=200.0, estado=Estado.INFECTADO)
        ind.infectar(tiempo_muerte=1)
        ind.actualizar_infeccion(prob_inmunidad=0.0, prob_infeccion=0.05)
        assert ind.estado == Estado.MUERTO

    def test_propiedad_vivo_sano(self) -> None:
        ind = Individuo(x=100.0, y=200.0, estado=Estado.SANO)
        assert ind.vivo

    def test_propiedad_vivo_muerto(self) -> None:
        ind = Individuo(x=100.0, y=200.0, estado=Estado.MUERTO)
        assert not ind.vivo

    def test_propiedad_posicion(self) -> None:
        ind = Individuo(x=100.0, y=200.0)
        assert ind.posicion == (100.0, 200.0)

    def test_prob_reinfeccion_despues_de_inmunidad(self) -> None:
        ind = Individuo(x=100.0, y=200.0, estado=Estado.INFECTADO)
        ind.infectar(tiempo_muerte=450)
        ind.actualizar_infeccion(prob_inmunidad=1.0, prob_infeccion=0.2)
        assert ind.estado == Estado.INMUNE
        assert 0 < ind.prob_reinfeccion <= 0.2
