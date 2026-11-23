from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from kinich.clima import (
    ErrorClima,
    cargar_perfil,
    cierre_componentes,
    posicion_solar,
    preparar_perfil,
    separar_componentes,
)

RUTA_CLIMA = Path(__file__).resolve().parents[1] / "data" / "clima_2019_2023_288.csv"


@pytest.fixture(scope="module")
def perfil():
    return preparar_perfil(RUTA_CLIMA)


@pytest.fixture(scope="module")
def df_clima():
    return cargar_perfil(RUTA_CLIMA)


# --- Carga y validación -----------------------------------------------------


def test_carga_288_filas_ordenadas(df_clima):
    assert len(df_clima) == 288
    assert df_clima["mes"].iloc[0] == 1 and df_clima["hora"].iloc[0] == 0
    assert df_clima["mes"].iloc[-1] == 12 and df_clima["hora"].iloc[-1] == 23


def test_rechaza_columna_faltante(tmp_path, df_clima):
    ruta = tmp_path / "sin_dhi.csv"
    df_clima.drop(columns="DHI").to_csv(ruta, index=False)
    with pytest.raises(ErrorClima, match="Faltan columnas"):
        cargar_perfil(ruta)


def test_rechaza_filas_incompletas(tmp_path, df_clima):
    ruta = tmp_path / "corto.csv"
    df_clima.iloc[:-1].to_csv(ruta, index=False)
    with pytest.raises(ErrorClima, match="288"):
        cargar_perfil(ruta)


def test_rechaza_irradiancia_negativa(tmp_path, df_clima):
    ruta = tmp_path / "negativo.csv"
    malo = df_clima.copy()
    malo.loc[100, "GHI"] = -1.0
    malo.to_csv(ruta, index=False)
    with pytest.raises(ErrorClima, match="negativas"):
        cargar_perfil(ruta)


def test_rechaza_mes_hora_duplicado(tmp_path, df_clima):
    ruta = tmp_path / "duplicado.csv"
    malo = df_clima.copy()
    malo.loc[1, "hora"] = 0
    malo.to_csv(ruta, index=False)
    with pytest.raises(ErrorClima, match="12 × 24"):
        cargar_perfil(ruta)


# --- Posición solar ---------------------------------------------------------


def test_sol_bajo_horizonte_de_noche(perfil):
    assert (perfil.elevacion[:, 0:5] < 0).all()
    assert (perfil.elevacion[:, 20:24] < 0).all()


def test_mediodia_sol_alto_y_hacia_el_sur_en_enero(perfil):
    assert perfil.elevacion[0, 12] > 45
    assert 150 < perfil.azimut[0, 12] < 210


def test_en_junio_el_sol_pasa_al_norte_al_mediodia(perfil):
    # Latitud 16.6° N: en junio el sol culmina al norte del cenit.
    assert perfil.elevacion[5, 12] > 80
    assert perfil.azimut[5, 12] > 270 or perfil.azimut[5, 12] < 90


def test_maximo_de_ghi_cerca_del_mediodia_solar(perfil):
    hora_max = perfil.ghi.argmax(axis=1)
    assert set(hora_max) <= {11, 12}


# --- Separación de componentes ----------------------------------------------


def test_separacion_sol_alto():
    bhi, dhi_ef = separar_componentes(
        np.array([600.0]), np.array([200.0]), np.array([40.0])
    )
    assert bhi[0] == pytest.approx(400.0)
    assert dhi_ef[0] == pytest.approx(200.0)


def test_separacion_sol_bajo_todo_difuso():
    bhi, dhi_ef = separar_componentes(
        np.array([20.0]), np.array([5.0]), np.array([4.9])
    )
    assert bhi[0] == 0.0
    assert dhi_ef[0] == pytest.approx(20.0)


def test_separacion_dhi_mayor_que_ghi_se_limita():
    bhi, dhi_ef = separar_componentes(
        np.array([10.0]), np.array([12.0]), np.array([30.0])
    )
    assert bhi[0] == 0.0
    assert dhi_ef[0] == pytest.approx(10.0)


def test_componentes_suman_ghi_en_todo_el_perfil(perfil):
    np.testing.assert_allclose(perfil.bhi + perfil.dhi_ef, perfil.ghi, atol=1e-9)
    assert (perfil.bhi >= 0).all() and (perfil.dhi_ef >= 0).all()


def test_noche_sin_irradiancia(perfil):
    noche = perfil.elevacion < 0
    assert (perfil.bhi[noche] == 0).all()


# --- Comprobaciones documentadas en docs/ -----------------------------------


def test_irradiacion_anual_ghi(perfil):
    assert perfil.irradiacion_anual_ghi() == pytest.approx(1949.33, abs=0.05)


def test_horas_de_sol_bajo_y_su_aporte(perfil):
    bajo = perfil.sol_bajo
    assert bajo.sum() == 16
    assert perfil.ghi[bajo].max() == pytest.approx(27.74, abs=0.01)
    aporte = (perfil.ghi * bajo).sum(axis=1) @ perfil.dias_mes / 1000
    assert aporte / perfil.irradiacion_anual_ghi() < 0.003


def test_mitad_de_hora_es_el_mejor_instante(df_clima):
    _, rms_inicio = cierre_componentes(df_clima, 0.0)
    sesgo_mitad, rms_mitad = cierre_componentes(df_clima, 0.5)
    _, rms_final = cierre_componentes(df_clima, 1.0)
    assert rms_mitad < rms_inicio and rms_mitad < rms_final
    # DHI + DNI·sin α queda por debajo de GHI: justifica usar GHI − DHI.
    assert sesgo_mitad < 0


def test_posicion_solar_forma():
    elevacion, azimut = posicion_solar()
    assert elevacion.shape == (12, 24) and azimut.shape == (12, 24)
    assert pd.notna(elevacion).all() and pd.notna(azimut).all()
