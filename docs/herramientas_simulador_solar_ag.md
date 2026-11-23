# K'inich — Herramientas del simulador 3D de optimización fotovoltaica con AG

**Tipo:** aplicación de escritorio · **Lenguaje:** Python 3.11 (entorno virtual) · **Enfoque:** edición 2D, visualización 3D y optimización mediante algoritmo genético (AG).

## 1. Herramientas y finalidad

| Herramienta | Uso en el proyecto |
|---|---|
| **PySide6 (Qt Widgets)** | Ventanas, pestañas, controles y tablas editables. |
| **QGraphicsView + QGraphicsScene** *(PySide6)* | Editor 2D de techo, dimensiones, obstáculos y rejilla. |
| **PyVista + pyvistaqt** | Vista 3D interactiva de techo, paneles, obstáculos, sol y sombras. |
| **NumPy** | Rejilla de ocupación, máscaras de sombra, energía, restricciones y aptitud. **Fuente de verdad geométrica del AG.** |
| **Shapely** | Editar polígonos y convertir techo y obstáculos a la rejilla; no interviene en la aptitud. |
| **pvlib** | Posición solar e irradiancia; comprobación de fórmulas fotovoltaicas (**ver sección 5**). |
| **pandas** | Procesar el CSV horario 2019–2023, convertir UTC a hora local y generar el perfil climático de 288 registros. |
| **AG propio o DEAP** | Torneo, cruza BLX-α, mutación gaussiana, elitismo y seguimiento generacional. Elegir según el profesor. |
| **QThread + señales de Qt** | Ejecutar el AG sin congelar la interfaz; reportar avances, pausa y cancelación. |
| **pyqtgraph** | Gráficas en vivo de aptitud y objetivos por generación. |
| **SQLite (`sqlite3`)** | Almacenar climas, paneles, costos, escenarios y resultados. |
| **requests** *(opcional para clima)* | Automatizar nuevas descargas de NASA POWER si se desea; consultar PVWatts (**ver sección 5**). Los datos históricos ya se descargaron desde el visor web. |
| **pytest** | Pruebas automáticas del modelo, las restricciones y el AG (**ver sección 5**). |
| **imageio + imageio-ffmpeg** | Exportar video del mejor individuo de cada generación, al terminar. |
| **PyInstaller** | Distribuir la aplicación en modo `--onedir` (**ver sección 5**). |
| **Git + GitHub** | Control de versiones y colaboración. |
| **`requirements.txt`** | Fijar versiones de dependencias comprobadas. |

## 2. Decisiones técnicas

1. **AG:** escribir un ciclo propio para elitismo, progreso y pausa, incluso si se usan operadores de DEAP. Después de cruza y mutación, limitar cada gen a su rango; redondear `N` al decodificar. Preguntar si el profesor permite DEAP.
2. **Geometría:** convertir los polígonos del editor a una **única rejilla NumPy** antes de optimizar. El AG solo evalúa esa rejilla; Shapely no se ejecuta por individuo.
3. **Sombras:** Python calcula su efecto energético; PyVista únicamente lo representa en 3D.
4. **Video:** guardar cromosoma y métricas del mejor individuo de cada generación; renderizar fotogramas **después** del AG, no durante la búsqueda.
5. **Datos:** SQLite es la fuente de trabajo y CSV solo sirve para importar/exportar. Asociar a cada corrida un hash SHA-256 de entradas y parámetros, más la versión del modelo, para detectar resultados desactualizados.
6. **Reproducibilidad:** registrar semilla, parámetros y versiones; fijar `random` y NumPy (o usar `numpy.random.Generator` de forma controlada).
7. **Hilos y compatibilidad:** actualizar Qt/PyVista solo desde el hilo principal mediante señales; pausar entre generaciones. Probar temprano la integración **Qt + VTK + OpenGL** en el equipo de exposición.
8. **Comprobación física y fuentes externas:** distinguir pruebas de implementación y validación independiente (**ver sección 5**).

## 3. Fuente climática: NASA POWER — datos obtenidos

**Estado: descargados, verificados y procesados.** Se utilizó el **[Data Access Viewer (DAV)](https://power.larc.nasa.gov/data-access-viewer/)** de NASA POWER, sin programar consultas a la API. La fuente es una estimación regional, no una estación meteorológica del techo.

| Concepto | Resultado |
|---|---|
| Coordenadas descargadas | **16.63° N, −93.09°** (punto de referencia cercano al campus; comprobar techo exacto antes del estudio definitivo). |
| Periodo original | **01/01/2019–31/12/2023**; resolución **horaria**, tiempo **UTC**. |
| Archivo original | `POWER_Point_Hourly_20190101_20231231_016d63N_093d09W_UTC.csv` |
| Cobertura y calidad | **43,824 horas** (incluye 2020 bisiesto); sin horas duplicadas, interrupciones, nulos ni `-999` en las cuatro variables. |
| Archivo para el AG | `clima_2019_2023_288.csv` — **288 filas** y columnas `mes,hora,GHI,DNI,DHI,T_amb`. |

| Variable | Parámetro original | Unidad en el CSV de NASA |
|---|---|---|
| GHI | `ALLSKY_SFC_SW_DWN` | Wh/m² por hora |
| DNI | `ALLSKY_SFC_SW_DNI` | Wh/m² por hora |
| DHI | `ALLSKY_SFC_SW_DIFF` | Wh/m² por hora |
| Temperatura ambiente | `T2M` | °C |

**Tratamiento realizado con pandas:** convertir de UTC a hora estándar de Chiapas (**UTC−6**), conservar las fechas locales de 2019–2023, agrupar por **mes y hora**, y promediar cada variable. La conversión deja **43,818 registros dentro del periodo local**: seis horas iniciales pasan al 31/12/2018 y se excluyen. Los valores de radiación son energía por intervalo de una hora (Wh/m²); su **valor numérico coincide con la irradiancia media de esa hora en W/m²**, como requiere la fórmula de potencia.

**Tratamiento de irradiancia en el modelo (no en el formulario):** usar `BHI = max(0, GHI − DHI)` (W/m²) para la **componente directa horizontal**; **BHI no es DNI**. Los datos originales GHI, DNI y DHI se conservan sin modificar. En 13 horas de amanecer y atardecer del perfil la DHI supera a la GHI (como máximo por 2.4 W/m²); el modelo usa `min(DHI, GHI)`, de modo que siempre se cumple `BHI + DHI_ef = GHI`.

- **Sol bajo:** para elevación **`α < 5°`** (`sin(α) < 0.087`), no dividir entre `sin(α)`; usar `BHI_ef = 0` y `DHI_ef = GHI`. Para `α ≥ 5°`, estimar `DNI_est = BHI / sin(α)`; el factor de división no supera **≈11.5**. Con este umbral, **16 de las 288 horas** del perfil se tratan como difusas (GHI ≤ **27.7 W/m²** cada una), y representan el **0.27 %** de la irradiación anual; el efecto de la aproximación es despreciable.
- **Posición solar:** calcularla en el **punto medio del intervalo** (`hora + 30 min`). Comprobado con pvlib (`kinich.clima.cierre_componentes`, día 15 de cada mes, horas con GHI ≥ 50 W/m²; prueba `test_mitad_de_hora_es_el_mejor_instante`): este instante reproduce mejor `GHI ≈ DHI + DNI · sin(α)`, con **RMS 35.9 W/m²**, frente a **46.7 W/m²** al inicio y **48.2 W/m²** al final de la hora.
- **Por qué no usar la DNI directamente:** en la misma comprobación con pvlib, `DHI + DNI · sin(α)` fue en promedio **27.0 W/m² (≈4 %) menor que GHI** durante las horas con radiación. Por consistencia con GHI se modela la componente horizontal directa como `GHI − DHI`, en lugar de utilizar la DNI del archivo para calcular la energía. La DNI original queda disponible para comprobaciones. Esta decisión prioriza conservar GHI; no constituye una validación independiente.

**Control de agregación:** GHI anual media en los datos originales: **1,950.41 kWh/m²**; reconstruida con el perfil de 288 filas, ponderado por los días de un año de 365 días: **1,949.33 kWh/m²** (**−0.056 %**). Esto verifica la conservación aproximada de la *irradiación GHI anual*, **no** el error de generación fotovoltaica. La comparación energética de 288 horas frente a la serie completa sigue pendiente (**ver sección 5**).

**Uso previsto:** el CSV reducido alimentará las evaluaciones rápidas del AG; el original se conservará para pruebas con las horas completas. Importar los datos validados a SQLite y mantener ambos archivos locales para operar sin internet. La resolución espacial oficial es regional (**1° × 1°** solar y **0.5° × 0.625°** meteorológica), por lo que no representa microclimas ni sombras del techo.

[Documentación NASA POWER](https://power.larc.nasa.gov/docs/services/) · [Acceso a datos horarios](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/).

## 4. Organización de la interfaz

- **Techo:** editor 2D con dimensiones, obstáculos y rejilla; visualización 3D sincronizada.
- **Climas:** gestionar perfiles, CSV y descarga opcional de NASA POWER.
- **Paneles y costos:** catálogos editables, presupuesto y selección del panel antes del AG.
- **Optimizar:** límites, pesos, semilla y operadores; ejecutar, pausar, cancelar y ver convergencia.
- **Resultados:** tres mejores diseños distintos, comparación de costos y energía, sombras por mes/hora, exportaciones y video.

## 5. Validación y despliegue

- **Pruebas unitarias (`pytest`):** geometría y márgenes, obstáculos, `N_col ≤ N`, recorte de genes, sombras en casos controlados, generación nocturna nula, energía no negativa y reproducibilidad. Comparar **DC** con `pvlib.pvsystem.pvwatts_dc` usando los mismos `G_i` (W/m²), `T_c` (°C), `P_stc` (W) y `mu` (1/°C), con tolerancia numérica definida. **Esto verifica la implementación de una fórmula equivalente, no valida el realismo del modelo.** Probar también pérdidas y recorte AC por separado; no se necesita `ModelChain` con módulos CEC.
- **Inversor:** se mantiene el supuesto original de eficiencia constante `η_inv = 0.96`. Como mejora opcional puede utilizarse `pvlib.inverter.pvwatts` (`η_nom = 0.96`), actualizando fórmula AC y pruebas. Compartir esa función tampoco constituye validación independiente.
- **Validación externa:** contrastar la configuración **sin obstáculos** con **[PVWatts V8](https://developer.nlr.gov/docs/solar/pvwatts/)** (API o calculadora). Registrar fecha, potencia, inclinación, azimut, relación DC/AC, pérdidas y datos de salida. Documentar que PVWatts puede usar clima TMY/NSRDB y otros modelos térmicos o de inversor, mientras el proyecto utiliza promedios NASA POWER 2019–2023. Una diferencia anual —incluso dentro de ±10 %— no demuestra por sí sola la precisión física si las entradas difieren.
- **Fidelidad del perfil climático:** comparar la **producción fotovoltaica calculada con 288 registros** frente a la calculada con la **serie horaria completa** de 2019–2023, manteniendo idéntica configuración. La diferencia de GHI (sección 3) no sustituye esta prueba.
- **Robustez:** realizar corridas con distintas semillas y reportar aptitud, tiempo y dispersión.
- **Despliegue:** empaquetar con `pyinstaller --onedir --windowed --name Kinich main.py` (ajustar el nombre de entrada). Copiar **toda la carpeta**. Probar en la computadora y el proyector reales la apertura, OpenGL, rotación/zoom, sombras, gráficas, CSV, AG, pausa y exportación; evitar depender del escritorio remoto.

## 6. Orden de desarrollo

1. **Completado:** descarga, revisión y reducción del clima 2019–2023 (sección 3).
2. Rejilla NumPy y modelo energético con pruebas.
3. AG y resultados, sin interfaz.
4. SQLite, catálogos e importación de CSV.
5. Editor 2D, visualizador 3D y gráficas.
6. Comparación energética, validación externa, video y empaquetado.

## Referencias técnicas

- [DEAP — operadores](https://deap.readthedocs.io/en/latest/api/tools.html)
- [PyVistaQt](https://qt.pyvista.org/)
- [pvlib — `pvwatts_dc`](https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.pvsystem.pvwatts_dc.html)
- [pvlib — inversor `pvwatts`](https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.inverter.pvwatts.html)
- [PVWatts V8 — API](https://developer.nlr.gov/docs/solar/pvwatts/)
- [NLR — aviso de transición](https://developer.nlr.gov/docs/nlr-domain-transition/) — `developer.nlr.gov` reemplaza al dominio antiguo (`developer.nrel.gov`, retirado el 29/05/2026); enlaces comprobados el 21/11/2026.
- [PyInstaller — modos de operación](https://pyinstaller.org/en/stable/operating-mode.html)
