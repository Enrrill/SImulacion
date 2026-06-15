import pytest

from src.configuracion import Estado, ConfigSimulacion
from src.simulacion.motor import MotorSimulacion


def _config_basica() -> ConfigSimulacion:
    return ConfigSimulacion(
        num_individuos=100,
        num_infectados_iniciales=3,
        radio_infeccion=50,
        prob_infeccion=0.5,
        prob_inmunidad=0.0,
        tiempo_muerte=1000,
    )


class TestMotorSimulacion:
    def test_reiniciar_crea_poblacion(self) -> None:
        motor = MotorSimulacion()
        cfg = _config_basica()
        motor.reiniciar(cfg)
        assert len(motor.poblacion) == cfg.num_individuos
        assert motor.ejecutando
        assert motor.frames_transcurridos == 0

    def test_reiniciar_infectados_iniciales(self) -> None:
        motor = MotorSimulacion()
        cfg = _config_basica()
        motor.reiniciar(cfg)
        infectados = sum(1 for ind in motor.poblacion if ind.estado == Estado.INFECTADO)
        assert infectados == cfg.num_infectados_iniciales

    def test_avanzar_incrementa_frames(self) -> None:
        motor = MotorSimulacion()
        cfg = _config_basica()
        motor.reiniciar(cfg)
        motor.avanzar(cfg)
        assert motor.frames_transcurridos == 1

    def test_avanzar_disminuye_susceptibles(self) -> None:
        motor = MotorSimulacion()
        cfg = ConfigSimulacion(
            num_individuos=100,
            num_infectados_iniciales=3,
            radio_infeccion=200,
            prob_infeccion=1.0,
            prob_inmunidad=0.0,
            tiempo_muerte=1000,
        )
        motor.reiniciar(cfg)
        stats = motor.avanzar(cfg)
        assert stats[Estado.SANO] < cfg.num_individuos - cfg.num_infectados_iniciales

    def test_historial_crece_con_cada_paso(self) -> None:
        motor = MotorSimulacion()
        cfg = _config_basica()
        motor.reiniciar(cfg)
        motor.avanzar(cfg)
        motor.avanzar(cfg)
        assert len(motor.historial[Estado.SANO]) == 2

    def test_epidemia_termina_sin_infectados(self) -> None:
        motor = MotorSimulacion()
        cfg = ConfigSimulacion(
            num_individuos=10,
            radio_infeccion=200,
            prob_infeccion=0.0,
            prob_inmunidad=0.0,
            tiempo_muerte=1,
        )
        motor.reiniciar(cfg)
        for _ in range(100):
            stats = motor.avanzar(cfg)
            if not motor.ejecutando:
                break
        assert stats[Estado.INFECTADO] == 0
        assert not motor.ejecutando

    def test_avanzar_con_motor_detenido_retorna_estadisticas(self) -> None:
        motor = MotorSimulacion()
        cfg = _config_basica()
        motor.reiniciar(cfg)
        motor.ejecutando = False
        stats = motor.avanzar(cfg)
        assert isinstance(stats, dict)
        assert set(stats.keys()) == {Estado.SANO, Estado.INFECTADO, Estado.INMUNE, Estado.MUERTO}

    def test_reiniciar_limpia_historial(self) -> None:
        motor = MotorSimulacion()
        cfg = _config_basica()
        motor.reiniciar(cfg)
        motor.avanzar(cfg)
        motor.reiniciar(cfg)
        assert len(motor.historial[Estado.SANO]) == 0

    def test_obtener_estadisticas_retorna_conteos(self) -> None:
        motor = MotorSimulacion()
        cfg = _config_basica()
        motor.reiniciar(cfg)
        stats = motor.obtener_estadisticas()
        total = sum(stats.values())
        assert total == cfg.num_individuos

    def test_estado_inicial_coincide_con_reinicio(self) -> None:
        motor = MotorSimulacion()
        cfg = _config_basica()
        motor.reiniciar(cfg)
        inicial = motor.estado_inicial
        assert inicial[Estado.SANO] == cfg.num_individuos - cfg.num_infectados_iniciales
        assert inicial[Estado.INFECTADO] == cfg.num_infectados_iniciales
        assert inicial[Estado.INMUNE] == 0
        assert inicial[Estado.MUERTO] == 0

    def test_estado_inicial_no_cambia_con_avanzar(self) -> None:
        motor = MotorSimulacion()
        cfg = _config_basica()
        motor.reiniciar(cfg)
        inicial = dict(motor.estado_inicial)
        motor.avanzar(cfg)
        assert motor.estado_inicial == inicial
