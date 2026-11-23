# K'inich — Modelo matemático y algoritmo genético

Definición completa del modelo que evalúa cada individuo. Este documento manda sobre el código: si algo cambia aquí, se actualizan el código y las pruebas.

## 1. Supuestos fijos

| Supuesto | Valor |
|---|---|
| Ubicación del clima | NASA POWER, punto 16.63° N, 93.09° O (campus UP Chiapas, Suchiapa) |
| Hora | Estándar local UTC−6 (sin horario de verano) |
| Clima | Perfil de 12 meses × 24 horas (`data/clima_2019_2023_288.csv`), promedio 2019–2023 |
| Día representativo | Día 15 de cada mes, para la posición solar |
| Instante de cálculo | Mitad de cada hora (hora + 30 min) |
| Panel | Un modelo del catálogo, elegido antes de correr el AG (no es variable de decisión) |
| Colocación | Vertical: lado largo *L* sobre la inclinación, ancho *W* a lo largo de la fila; 2 cm entre paneles |
| Albedo | ρ = 0.2 |
| Pérdidas de cableado y suciedad | η_p = 0.90 |
| Eficiencia del inversor | η_inv = 0.96 (constante) |
| Margen al borde del techo | 0.6 m |
| Umbral de sol bajo | α < 5° |

## 2. Cromosoma y decodificación

**Cromosoma:** vector real **x = [N, β, γ, d, R]**. *N* se redondea al decodificar.

**Decodificador (determinista):**

1. Distancia entre frentes de filas consecutivas: p = L·cos β + d.
2. Se rota la rejilla (γ − 180°) para que las filas queden perpendiculares a la orientación.
3. Se llenan filas desde el borde frontal hacia atrás y, dentro de cada fila, de izquierda a derecha.
4. Un panel se coloca solo si todas las celdas de su huella están disponibles: dentro del techo, fuera de obstáculos, fuera del margen y sin ocupar.
5. Se detiene al colocar *N* paneles, al agotarse el espacio o cuando un panel más haría que C > B o q > q_max. **N_col** = paneles realmente colocados; energía, costo, inversor y carga se calculan con N_col.

## 3. Geometría solar e irradiancia

- α: elevación solar; A_s: azimut solar. Se calculan con pvlib para el día 15 de cada mes a la mitad de cada hora.
- Ángulo de incidencia sobre el panel:

  cos θ = sin α · cos β + cos α · sin β · cos(A_s − γ)

**Separación de componentes** (se usa GHI − DHI en lugar de la DNI del archivo; ver la justificación en la sección 3 del documento de herramientas):

- Si α ≥ 5°: BHI = max(0, GHI − DHI), DHI_ef = min(DHI, GHI)
- Si α < 5°: BHI = 0, DHI_ef = GHI (toda la irradiancia se trata como difusa)

**Irradiancia sobre el panel *i*:**

G_i = BHI · max(0, cos θ) / sin α · (1 − s_i) + DHI_ef · (1 + cos β)/2 + GHI · ρ · (1 − cos β)/2

(con α < 5° el primer término vale 0 y no se divide). En todos los casos BHI + DHI_ef = GHI.

## 4. Sombras

**Entre filas** (solo si hay un panel justo enfrente y cos(A_s − γ) > 0):

- Ángulo del perfil solar: tan α_p = tan α / cos(A_s − γ)
- Fracción sombreada: s_fila = clip(1 − p · sin α_p / (L · sin(α_p + β)), 0, 1)
- Casos de control: con β = 0 o con el sol en el cenit, s_fila = 0.

**Por obstáculos:**

- Para cada hora se precalcula una máscara de la rejilla: cada obstáculo de altura H proyecta una sombra de largo H / tan α en dirección opuesta al sol.
- s_obs = fracción de las celdas de la huella del panel que quedan en sombra.
- La máscara no depende del individuo; se calcula una vez por escenario.

**Combinada:** s_i = 1 − (1 − s_fila)(1 − s_obs)

## 5. Potencia y energía

- Temperatura de celda: T_c = T_a + (NOCT − 20)/800 · G_i
- Potencia DC del panel: P_i = P_stc · (G_i/1000) · [1 + μ(T_c − 25)]
- Potencia nominal del inversor: P_inv = N_col · P_stc / R
- Potencia AC: P_AC = min(η_inv · η_p · Σ_i P_i, P_inv)
- Energía del mes *m*: E_m = días_m · Σ_h P_AC(m, h) / 1000 (kWh)

## 6. Objetivos

| Objetivo | Definición | Caso especial |
|---|---|---|
| **E** (maximizar) | Σ_m E_m (kWh/año) | — |
| **C** (minimizar) | N_col · (c_panel + c_estructura + c_instalación) + c_inv · P_inv/1000 (MXN) | — |
| **S** (minimizar) | 100 · (E⁰ − E)/E⁰, donde E⁰ es la energía sin sombras (%) | Si E⁰ = 0 → S = 100 |
| **V** (minimizar) | σ(E_m)/μ(E_m), coeficiente de variación mensual | Si μ = 0 → V = 1 |

Se usa el coeficiente de variación y no la desviación estándar porque esta crece con el tamaño del sistema y quedaría correlacionada con *E*.

Carga sobre el techo: q = N_col · (m_panel + m_estructura) / A_útil (kg/m²)

## 7. Normalización y aptitud

- Ê = min(1, E / E_ref), con E_ref = N_teo · (P_stc/1000) · H_GHI
  - N_teo = ⌊A_útil / (L·W)⌋
  - H_GHI = irradiación global anual del perfil (1,949.3 kWh/m²)
- Ĉ = C / B (B = presupuesto)
- Ŝ = S / 100
- V̂ = min(1, V)

**Aptitud:**

f = Ê · 1/(1 + Ĉ) · 1/(1 + Ŝ) · 1/(1 + V̂)

- Las restricciones no entran en la aptitud: las garantiza el decodificador (secciones 2 y 8), por lo que Ĉ ∈ [0, 1].
- **Sin división entre cero:** todos los denominadores son ≥ 1 o constantes positivas (B, E_ref, A_útil), que se validan antes de ejecutar el AG; E⁰ = 0 y μ = 0 tienen caso definido.
- Rango: f ∈ [0, 1].

## 8. Restricciones

**Espacio de búsqueda** (se garantiza recortando los genes tras cruza y mutación):

X = {(N, β, γ, d, R) | N ∈ ℤ, 1 ≤ N ≤ N_teo; β ∈ [5°, 45°]; γ ∈ [90°, 270°]; d ∈ [0.6, 5.0] m; R ∈ [1.0, 1.5]}

- β ≥ 5° para que la lluvia limpie los paneles.

**Conjunto factible del acomodo decodificado** (lo garantiza el decodificador):

F = {x ∈ X | 0 ≤ N_col(x) ≤ N, C(x) ≤ B, q(x) ≤ q_max}

**Geométricas** (las garantiza el decodificador):

- ∀ panel i: Celdas(i) ⊆ Techo \ (Obstáculos ∪ Margen)
- ∀ i ≠ j: Celdas(i) ∩ Celdas(j) = ∅

## 9. Algoritmo genético

| Elemento | Valor |
|---|---|
| Codificación | Real, 5 genes |
| Población | 60, inicialización uniforme dentro de los rangos |
| Selección | Torneo, k = 3 |
| Cruza | BLX-α, α = 0.5, p_c = 0.9 |
| Mutación | Gaussiana, p_m = 0.2 por gen, σ = 10 % del rango del gen |
| Elitismo | 2 mejores |
| Paro | 100 generaciones, o 25 generaciones sin mejora > 0.1 % |
| Semilla | Configurable |
| Top 3 | Distintos entre sí: distancia normalizada > 0.05 |

**Justificación frente a fuerza bruta:** discretizando (N ≤ 200, β cada 1°, γ cada 1°, d cada 0.1 m, R cada 0.01) hay ≈ 200 × 41 × 181 × 45 × 51 ≈ 3.4 × 10⁹ combinaciones. A 10 ms por evaluación serían más de un año; el AG usa ≈ 6,000 evaluaciones.

## 10. Configuración de referencia (línea base de instalador)

β = 17° (≈ latitud), γ = 180°, el máximo de paneles que quepa, R = 1.2, d según la regla de no sombra al mediodía del solsticio de invierno. El AG debe superarla en *f*; se reporta la mejora en % de cada objetivo.

## 11. Limitaciones declaradas

- La sombra parcial se modela lineal; los diodos de derivación reales la empeoran, así que el modelo es optimista.
- Se usa un perfil promedio de 288 horas, no la serie completa (pendiente la prueba de fidelidad, ver herramientas §5).
- Los obstáculos se proyectan a nivel del techo; no se considera la altura del panel.
- El clima es una estimación satelital regional (≈ 1° × 1°), no una medición en el techo.
- Eficiencia del inversor constante (mejora opcional: `pvlib.inverter.pvwatts`).
