# K'inich — Datos

## Archivos

| Archivo | Estado | Descripción |
|---|---|---|
| `clima_2019_2023_288.csv` | ✅ Listo | Perfil climático de 288 filas (12 meses × 24 horas) |
| `techo.csv` | ⏳ Plantilla vacía | Rejilla del techo y obstáculos |
| `paneles.csv` | ⏳ Plantilla vacía | Catálogo de paneles comerciales |
| `costos.csv` | ⏳ Plantilla vacía | Costos unitarios y presupuesto |
| `POWER_Point_Hourly_20190101_20231231_016d63N_093d09W_UTC.csv` | ⏳ Falta copiar | Serie horaria original de NASA POWER (43,824 h) |

## clima_2019_2023_288.csv

- **Fuente:** NASA POWER, Data Access Viewer, punto 16.63° N, 93.09° O, comunidad RE.
- **Periodo:** 2019–2023, horario, convertido de UTC a hora local UTC−6 y promediado por mes y hora.
- **Etiqueta de hora:** la hora indica el inicio del intervalo; el valor es el promedio de esa hora. La posición solar se calcula a la mitad (hora + 30 min).

| Columna | Unidad | Descripción |
|---|---|---|
| `mes` | 1–12 | Mes |
| `hora` | 0–23 | Hora local de inicio del intervalo |
| `GHI` | W/m² | Irradiancia global horizontal (media de la hora) |
| `DNI` | W/m² | Irradiancia directa normal (solo referencia; el modelo usa GHI − DHI) |
| `DHI` | W/m² | Irradiancia difusa horizontal |
| `T_amb` | °C | Temperatura ambiente a 2 m |

**Comprobaciones hechas:** 288 filas, sin vacíos ni negativos; GHI anual reconstruida = 1,949.3 kWh/m² (−0.056 % frente a la serie original). Máximo diario en marzo–abril (≈ 6.1–6.3 kWh/m²·día) y mínimo en noviembre (≈ 4.2).

## Plantillas por llenar

### techo.csv

Una fila por celda de la rejilla. Lo generará el editor 2D, pero puede llenarse a mano para las primeras pruebas.

| Columna | Unidad | Descripción |
|---|---|---|
| `x_m`, `y_m` | m | Centro de la celda |
| `disponible` | 0/1 | 1 si la celda es parte del techo y no es obstáculo |
| `altura_obs_m` | m | Altura del obstáculo (0 si no hay) |

### paneles.csv

| Columna | Unidad | Descripción |
|---|---|---|
| `modelo` | — | Marca y modelo |
| `P_stc_W` | W | Potencia nominal en STC |
| `L_m`, `W_m` | m | Largo y ancho |
| `NOCT_C` | °C | Temperatura nominal de operación de la celda |
| `mu_pct_C` | %/°C | Coeficiente de temperatura de potencia (negativo) |
| `masa_kg` | kg | Masa del panel |
| `precio_MXN` | MXN | Precio unitario |
| `fuente` | — | Distribuidor o URL de la ficha |
| `fecha_consulta` | AAAA-MM-DD | Fecha de la cotización |

### costos.csv

| Columna | Descripción |
|---|---|
| `concepto` | `estructura_por_panel`, `instalacion_por_panel`, `inversor_por_kW`, `masa_estructura_por_panel`, `presupuesto`, `q_max` |
| `valor` | Valor numérico |
| `unidad` | MXN, MXN/kW, kg o kg/m² |
| `fuente` | Cotización, distribuidor o "supuesto" |
| `fecha_consulta` | AAAA-MM-DD |
