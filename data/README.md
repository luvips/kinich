# K'inich — Datos

## Archivos

| Archivo | Estado | Descripción |
|---|---|---|
| `clima_2019_2023_288.csv` | ✅ Listo | Perfil climático de 288 filas (12 meses × 24 horas) |
| `techo.csv` | ⏳ Pendiente de generar / medir | Rejilla del techo y obstáculos |
| `paneles.csv` | ✅ 3 modelos homologados con ficha y precio publicado | Catálogo de paneles comerciales |
| `costos.csv` | ✅ Completo (con referencias de mercado y normativa para Chiapas) | Costos unitarios, masas, carga admisible y presupuesto |
| `POWER_Point_Hourly_20190101_20231231_016d63N_093d09W_UTC.csv` | ⏳ Falta copiar | Serie horaria original de NASA POWER (43,824 h) |

## clima_2019_2023_288.csv

- **Fuente:** NASA POWER, Data Access Viewer, punto 16.63° N, 93.09° O, comunidad RE (el campus de la UP Chiapas en Suchiapa se ubica en 16.6155° N, 93.0895° O, dentro de la misma celda satelital de NASA POWER).
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

## Catálogos y caso de prueba

### techo.csv

Una fila por celda de la rejilla. Lo generará el editor 2D; el archivo actual es un caso supuesto mientras se elige el edificio.

| Columna | Unidad | Descripción |
|---|---|---|
| `x_m`, `y_m` | m | Centro de la celda |
| `disponible` | 0/1 | 1 si la celda es parte del techo y no es obstáculo |
| `altura_obs_m` | m | Altura del obstáculo (0 si no hay) |

**Caso supuesto (no medido):** techo plano de 30 × 20 m con celdas de 0.2 m (15,000 filas). Origen en la esquina suroeste, +x al este y +y al norte. El margen de 0.6 m no está marcado en el archivo: lo aplica el decodificador.

| Obstáculo | x (m) | y (m) | Altura (m) |
|---|---|---|---|
| Tinaco 1 | 6.0–8.4 | 4.0–6.4 | 2.5 |
| Tinaco 2 | 20.0–22.4 | 5.0–7.4 | 2.5 |
| Domo | 13.0–16.0 | 10.0–13.0 | 0.8 |
| Ducto | 24.0–25.0 | 11.0–19.0 | 1.2 |
| Pretil | perímetro | 0.2 de espesor | 1.0 |

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

**Notas de los datos actuales:**

- Los precios son de menudeo con IVA en distribuidores nacionales, sin envío ni embalaje. Para entrega en Suchiapa, Chiapas (C.P. 29150, zona metropolitana de Tuxtla Gutiérrez), el flete consolidado en tarima añade aproximadamente 250–450 MXN por panel, o bien se adquieren con distribuidores locales en Tuxtla Gutiérrez (Kōmaru Solar, Galio, Solartiva, Velmon).
- `mu_pct_C` está en %/°C: se divide entre 100 antes de usarla en la fórmula de potencia.
- Jinko (`JKM475N-60HL4-V`): precio en oferta (precio normal, 2,420 MXN); todos los parámetros coinciden con la ficha Tiger Neo N-type 60HL4-V.
- Hanersun (`HN21RN-54HT500W`): homologado con la especificación oficial de la serie HiTouch 6N (`NOCT_C = 45 °C`, `masa_kg = 26.4 kg`; la página del distribuidor publicaba 42 °C y 26.5 kg). Es bifacial y se modela solo por la cara frontal.
- JA Solar (`JAM72S30-550/MR`): sin existencias al consultar en esa tienda. La tienda publica masas contradictorias (21 y 28 kg); se usó la de la ficha técnica enlazada (marco de 35 mm: `2.279 m`, `28.6 kg`).

### costos.csv

| Columna | Descripción |
|---|---|
| `concepto` | `estructura_por_panel`, `instalacion_por_panel`, `inversor_por_kW`, `masa_estructura_por_panel`, `presupuesto`, `q_max` |
| `valor` | Valor numérico |
| `unidad` | MXN, MXN/kW, kg o kg/m² |
| `fuente` | Cotización, distribuidor, normativa o "supuesto" |
| `fecha_consulta` | AAAA-MM-DD |

**Cómo se obtuvo cada valor (considerando Suchiapa / Zona Metropolitana de Tuxtla Gutiérrez, Chiapas):**

- `estructura_por_panel` (`802.50 MXN`): módulo de 4 paneles en aluminio anodizado 6005-T5/T6 = 2 rieles de 4.8 m (840 c/u) + 3 fijaciones frontales (120 c/u) + 3 traseras ajustables (290 c/u) + 4 abrazaderas finales (30 c/u) + 6 medias (30 c/u) = 3,210 MXN, entre 4 = 802.50 MXN. No incluye anclajes químicos, lastre, tierra física ni flete de perfilería larga a Chiapas (con herrajes de anclaje e impermeabilización o flete a Tuxtla/Suchiapa, el costo en sitio ronda 1,150–1,450 MXN/panel). **Nota técnica:** el soporte trasero cotizado en Enertik se ajusta de 15° a 30°; para ángulos menores o mayores del rango del AG ($\beta \in [5^\circ, 45^\circ]$) se asume ajuste equivalente de pata telescópica o perfil ranurado.
- `instalacion_por_panel` (`3150 MXN`): PSE (junio 2026) e integradores en Tuxtla Gutiérrez, Chiapas, reportan costos llave en mano de 18,000–24,000 MXN/kWp instalado, del que mano de obra es 12–18 %, material eléctrico (BOS: cableado solar, canalización, protecciones DC/AC) 10–12 % y trámites de interconexión CFE + traslado local (Tuxtla–Suchiapa, 21 km) 3–5 %. Con los puntos medios: 21,000 × 30 % × 0.5 kWp = 3,150 MXN por panel.
- `inversor_por_kW` (`2074.80 MXN/kW`): Growatt MID 25KTL3-XL2 de 25 kW (trifásico a 220 V, acorde a la red de baja tensión en edificios institucionales en México), 51,870 MXN con IVA, entre 25 kW. En el mercado mexicano (2025–2026), inversores equivalentes trifásicos 220 V de 25 kW (Growatt MID 25KTL3-X2, Solis S5-GC25K-LV) oscilan entre 48,000 y 65,000 MXN + IVA (2,100–2,700 MXN/kW con IVA). El modelo lo trata como costo continuo por kW.
- `masa_estructura_por_panel` (`5.5 kg`): masa por módulo de la estructura de montaje de aluminio anodizado 6005-T5/T6 para techo plano anclada a losa (2.4 m lineales de riel por panel ≈ 2.2 kg + proporción de soportes triangulares/telescópicos ≈ 2.1 kg + abrazaderas, tornillería de acero inoxidable y taquetes químicos ≈ 1.2 kg). *Nota:* si mantenimiento exigiera sistema lastrado sin perforar losa, los bloques de concreto para viento en Chiapas añadirían 30–40 kg/panel (total ≈ 38 kg/panel).
- `presupuesto` (`700000 MXN`): presupuesto de referencia para el caso de prueba institucional (permite instalar del orden de 90 a 105 paneles con estructura, inversor e instalación).
- `q_max` (`40.0 kg/m2`): carga permanente admisible sobre el área útil del techo. Fundamentada en el **Reglamento de Construcción para el Municipio de Tuxtla Gutiérrez, Chiapas** (referencia normativa en la ZM Tuxtla–Suchiapa) y las **NTC-CADEE**, que fijan para cubiertas y azoteas planas (pendiente ≤ 5 %) una carga viva máxima gravitacional $W_m = 100\text{ kg/m}^2$ y una carga viva instantánea para diseño sísmico/viento $W_a = 70\text{ kg/m}^2$. Al ubicarse Suchiapa en zona de alta sismicidad y requerirse reserva para tránsito de mantenimiento e impermeabilización, se establece un límite seguro de $40.0\text{ kg/m}^2$ para el sistema fotovoltaico.
