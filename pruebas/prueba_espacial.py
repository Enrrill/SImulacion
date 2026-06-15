import pytest
from src.simulacion.espacial import HashEspacial


class TestHashEspacial:
    def test_insertar_y_consultar_misma_celda(self) -> None:
        h = HashEspacial(tamanio_celda=30)
        h.insertar(0, 15.0, 15.0)
        h.insertar(1, 25.0, 25.0)
        vecinos = h.consultar_radio(20.0, 20.0, 20.0)
        assert 0 in vecinos
        assert 1 in vecinos

    def test_consultar_radio_filtra_distancia(self) -> None:
        h = HashEspacial(tamanio_celda=50)
        h.insertar(0, 10.0, 10.0)
        h.insertar(1, 100.0, 100.0)
        vecinos = h.consultar_radio(10.0, 10.0, 5.0)
        assert 0 in vecinos
        assert 1 not in vecinos

    def test_eliminar_remueve_elemento(self) -> None:
        h = HashEspacial(tamanio_celda=30)
        h.insertar(0, 15.0, 15.0)
        h.insertar(1, 25.0, 25.0)
        h.eliminar(0, 15.0, 15.0)
        vecinos = h.consultar_radio(20.0, 20.0, 20.0)
        assert 0 not in vecinos
        assert 1 in vecinos

    def test_actualizar_cambia_celda(self) -> None:
        h = HashEspacial(tamanio_celda=30)
        h.insertar(0, 10.0, 10.0)
        h.insertar(1, 200.0, 200.0)

        h.actualizar(0, 10.0, 10.0, 200.0, 200.0)
        vecinos_cerca = h.consultar_radio(10.0, 10.0, 20.0)
        assert 0 not in vecinos_cerca

        vecinos_lejos = h.consultar_radio(200.0, 200.0, 20.0)
        assert 0 in vecinos_lejos

    def test_actualizar_misma_celda_no_cambia(self) -> None:
        h = HashEspacial(tamanio_celda=30)
        h.insertar(0, 10.0, 10.0)
        h.insertar(1, 15.0, 15.0)

        h.actualizar(0, 10.0, 10.0, 20.0, 20.0)
        vecinos = h.consultar_radio(20.0, 20.0, 20.0)
        assert 0 in vecinos
        assert 1 in vecinos

    def test_limpiar_vacia_estructura(self) -> None:
        h = HashEspacial(tamanio_celda=30)
        h.insertar(0, 10.0, 10.0)
        h.insertar(1, 20.0, 20.0)
        h.limpiar()
        vecinos = h.consultar_radio(15.0, 15.0, 50.0)
        assert len(vecinos) == 0

    def test_eliminar_id_inexistente_no_falla(self) -> None:
        h = HashEspacial(tamanio_celda=30)
        h.eliminar(999, 10.0, 10.0)

    def test_insertar_multiples_en_consulta_radio(self) -> None:
        h = HashEspacial(tamanio_celda=30)
        for i in range(10):
            h.insertar(i, float(i * 10), 0.0)
        vecinos = h.consultar_radio(45.0, 0.0, 30.0)
        assert len(vecinos) >= 3
