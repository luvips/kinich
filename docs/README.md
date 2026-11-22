# K'inich — Documentación del proyecto

Proyecto de Inteligencia Artificial 7X (UP Chiapas): optimización con algoritmo genético del acomodo de paneles solares en techos del campus.

## Contenido

| Archivo | Qué contiene |
|---|---|
| `propuesta_formulario.md` | Respuestas del formulario de la propuesta, listas para copiar |
| `modelo_matematico.md` | Modelo completo: cromosoma, decodificador, fórmulas, aptitud, restricciones y AG |
| `herramientas_simulador_solar_ag.md` | Herramientas, decisiones técnicas, datos climáticos, validación y orden de desarrollo |
| `../data/` | Clima procesado y plantillas de los catálogos (ver `data/README.md`) |

## Para revisar antes de programar

Marquen cada punto cuando esté revisado o resuelto.

**Revisión del contenido**

- [ ] La propuesta (`propuesta_formulario.md`) es coherente con el modelo (`modelo_matematico.md`).
- [ ] Los rangos de las variables de decisión tienen sentido para un techo real.
- [ ] La función de aptitud y las restricciones se entienden y se pueden defender.
- [ ] El nombre K'inich queda aprobado por ambos.

**Decisiones pendientes**

- [ ] Preguntar al profesor si se permite DEAP o si el AG debe ser propio.
- [ ] Elegir el edificio y el techo concreto.

**Datos que faltan** (plantillas en `data/`)

- [ ] `techo.csv`: medir el techo y sus obstáculos (flexómetro + Google Earth, con fotos).
- [ ] `paneles.csv`: 3 paneles comerciales de 450–550 W, con ficha técnica en PDF y precio en MXN.
- [ ] `costos.csv`: 2 cotizaciones de estructura, instalación e inversor por kW.
- [ ] Capacidad de carga del techo (q_max): pedirla a mantenimiento o declarar un supuesto.

**Pendientes técnicos ya identificados**

- [ ] Repetir con pvlib la comprobación preliminar del clima (instante a mitad de hora y cierre GHI ≈ DHI + DNI·sin α).
- [ ] Conseguir el CSV horario original de NASA POWER y guardarlo en `data/` (necesario para la prueba de fidelidad del perfil de 288 horas).

## Siguiente paso

Cuando todo lo anterior esté revisado: paso 2 del orden de desarrollo, la rejilla NumPy y el modelo energético con sus pruebas.
