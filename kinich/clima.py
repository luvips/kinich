"""Perfil climático de 288 horas: carga, posición solar y separación de componentes.

Convenciones (ver docs/modelo_matematico.md, secciones 1 y 3):

- Hora local estándar UTC−6, sin horario de verano.
- La columna ``hora`` indica el inicio del intervalo; los valores son el promedio
  de esa hora. La posición solar se calcula a la mitad (hora + 30 min).
- Día representativo: el 15 de cada mes, en un año no bisiesto de referencia.
- Azimut solar en grados desde el norte, en sentido horario (180° = sur),
  la misma convención que el azimut γ de los paneles.
- Con elevación α < 5° toda la irradiancia se trata como difusa.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pvlib

COLUMNAS = ["mes", "hora", "GHI", "DNI", "DHI", "T_amb"]
MESES = 12
HORAS = 24

LATITUD = 16.63
LONGITUD = -93.09
ZONA_HORARIA = "Etc/GMT+6"  # UTC−6 fijo (el signo de Etc/GMT está invertido)
ANIO_REFERENCIA = 2023  # año no bisiesto
DIA_REPRESENTATIVO = 15
UMBRAL_SOL_BAJO_GRADOS = 5.0

DIAS_MES = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])


class ErrorClima(ValueError):
    """El archivo de clima no cumple el formato esperado."""


@dataclass(frozen=True)
class PerfilClimatico:
    """Perfil de 12 × 24 valores. Todas las matrices tienen forma (12, 24).

    Irradiancias en W/m², temperatura en °C y ángulos en grados.
    """

    ghi: np.ndarray
    dni: np.ndarray
    dhi: np.ndarray
    t_amb: np.ndarray
    elevacion: np.ndarray
    azimut: np.ndarray
    bhi: np.ndarray
    dhi_ef: np.ndarray
    dias_mes: np.ndarray
    latitud: float
    longitud: float

    @property
    def sol_bajo(self) -> np.ndarray:
        """Horas con irradiancia que se tratan como difusas por tener α < umbral."""
        return (self.ghi > 0) & (self.elevacion < UMBRAL_SOL_BAJO_GRADOS)

    def irradiacion_anual_ghi(self) -> float:
        """Irradiación global horizontal anual en kWh/m²."""
        return float((self.ghi.sum(axis=1) * self.dias_mes).sum() / 1000.0)


def cargar_perfil(ruta: str | Path) -> pd.DataFrame:
    """Lee y valida el CSV de 288 filas. Regresa las filas ordenadas por mes y hora."""
    df = pd.read_csv(ruta)

    faltantes = [c for c in COLUMNAS if c not in df.columns]
    if faltantes:
        raise ErrorClima(f"Faltan columnas: {faltantes}")
    if len(df) != MESES * HORAS:
        raise ErrorClima(f"Se esperaban {MESES * HORAS} filas y hay {len(df)}")
    if df[COLUMNAS].isna().any().any():
        raise ErrorClima("Hay valores vacíos")

    esperadas = {(m, h) for m in range(1, MESES + 1) for h in range(HORAS)}
    presentes = set(zip(df["mes"].astype(int), df["hora"].astype(int)))
    if presentes != esperadas:
        raise ErrorClima("Las combinaciones mes-hora no cubren exactamente 12 × 24")

    if (df[["GHI", "DNI", "DHI"]] < 0).any().any():
        raise ErrorClima("Hay irradiancias negativas")

    # En el perfil de NASA POWER hay 13 horas de amanecer/atardecer con DHI
    # ligeramente mayor que GHI (≤ 2.5 W/m²). No se rechazan: separar_componentes
    # limita DHI a GHI para que la difusa nunca supere a la global.
    return df.sort_values(["mes", "hora"]).reset_index(drop=True)


def _a_matriz(df: pd.DataFrame, columna: str) -> np.ndarray:
    return df[columna].to_numpy(dtype=float).reshape(MESES, HORAS)


def posicion_solar(
    latitud: float = LATITUD,
    longitud: float = LONGITUD,
    desfase_horas: float = 0.5,
) -> tuple[np.ndarray, np.ndarray]:
    """Elevación y azimut solares (grados) para el día 15 de cada mes.

    ``desfase_horas`` es el instante dentro de cada intervalo: 0 = inicio,
    0.5 = mitad (valor del modelo), 1 = final.
    """
    inicio = pd.Timestamp(ANIO_REFERENCIA, 1, DIA_REPRESENTATIVO, tz=ZONA_HORARIA)
    instantes = [
        inicio.replace(month=m) + pd.Timedelta(hours=h + desfase_horas)
        for m in range(1, MESES + 1)
        for h in range(HORAS)
    ]
    pos = pvlib.solarposition.get_solarposition(
        pd.DatetimeIndex(instantes), latitud, longitud
    )
    elevacion = pos["apparent_elevation"].to_numpy().reshape(MESES, HORAS)
    azimut = pos["azimuth"].to_numpy().reshape(MESES, HORAS)
    return elevacion, azimut


def separar_componentes(
    ghi: np.ndarray,
    dhi: np.ndarray,
    elevacion: np.ndarray,
    umbral_grados: float = UMBRAL_SOL_BAJO_GRADOS,
) -> tuple[np.ndarray, np.ndarray]:
    """Componente directa horizontal (BHI) y difusa efectiva (DHI_ef).

    - α ≥ umbral: BHI = max(0, GHI − DHI), DHI_ef = min(DHI, GHI)
    - α < umbral: BHI = 0, DHI_ef = GHI

    Siempre se cumple BHI + DHI_ef = GHI, así que la energía queda amarrada a GHI.
    """
    ghi = np.asarray(ghi, dtype=float)
    dhi = np.minimum(np.asarray(dhi, dtype=float), ghi)
    sol_bajo = np.asarray(elevacion) < umbral_grados
    bhi = np.where(sol_bajo, 0.0, np.maximum(0.0, ghi - dhi))
    dhi_ef = np.where(sol_bajo, ghi, dhi)
    return bhi, dhi_ef


def preparar_perfil(
    ruta: str | Path,
    latitud: float = LATITUD,
    longitud: float = LONGITUD,
) -> PerfilClimatico:
    """Carga el CSV y calcula la posición solar y las componentes del modelo."""
    df = cargar_perfil(ruta)
    ghi = _a_matriz(df, "GHI")
    dhi = _a_matriz(df, "DHI")
    elevacion, azimut = posicion_solar(latitud, longitud)
    bhi, dhi_ef = separar_componentes(ghi, dhi, elevacion)
    return PerfilClimatico(
        ghi=ghi,
        dni=_a_matriz(df, "DNI"),
        dhi=dhi,
        t_amb=_a_matriz(df, "T_amb"),
        elevacion=elevacion,
        azimut=azimut,
        bhi=bhi,
        dhi_ef=dhi_ef,
        dias_mes=DIAS_MES.copy(),
        latitud=latitud,
        longitud=longitud,
    )


def cierre_componentes(
    df: pd.DataFrame,
    desfase_horas: float,
    latitud: float = LATITUD,
    longitud: float = LONGITUD,
    ghi_minimo: float = 50.0,
) -> tuple[float, float]:
    """Comprueba GHI ≈ DHI + DNI·sin α para un instante dentro de la hora.

    Regresa (sesgo medio, RMS) de DHI + DNI·sin α − GHI en W/m², solo en horas
    con GHI ≥ ``ghi_minimo``. Sirve para justificar el instante a mitad de hora y
    el uso de GHI − DHI en lugar de la DNI del archivo.
    """
    elevacion, _ = posicion_solar(latitud, longitud, desfase_horas)
    ghi = _a_matriz(df, "GHI")
    dni = _a_matriz(df, "DNI")
    dhi = _a_matriz(df, "DHI")
    seno = np.maximum(0.0, np.sin(np.radians(elevacion)))
    error = (dhi + dni * seno - ghi)[ghi >= ghi_minimo]
    return float(error.mean()), float(np.sqrt((error**2).mean()))
