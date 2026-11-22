# K'inich — Propuesta (respuestas del formulario 2026.C3.07X.IA Aplicación AG)

> Texto listo para copiar en el formulario, campo por campo.
> *K'inich*: "soleado" o "del sol" en maya clásico; título de los gobernantes de Palenque, Chiapas.

## CONTEXTO DE LA PROBLEMÁTICA

La Universidad Politécnica de Chiapas se ubica en Suchiapa, en la zona metropolitana de Tuxtla Gutiérrez, una región con alta radiación solar durante todo el año, que alcanza su máximo en marzo y abril. Sin embargo, la energía disponible no es constante. En la temporada de lluvias, de mayo a octubre, la nubosidad reduce la radiación directa, y en invierno, de noviembre a enero, la menor altura del sol reduce la energía que llega a los techos.

Los techos de los edificios del campus son espacios que podrían aprovecharse para instalar paneles solares y reducir el consumo de energía de la red. Sin embargo, tienen dimensiones limitadas y obstáculos como tinacos, domos, ductos y pretiles, que proyectan sombra y reducen el área útil.

Diseñar una instalación implica decidir cuántos paneles colocar, con qué inclinación y orientación, a qué distancia entre filas y con qué capacidad de inversor. Cada decisión afecta la energía generada, el costo y la sombra que los propios paneles se proyectan entre sí. Normalmente estas decisiones se toman con reglas generales del instalador, sin evaluar las combinaciones posibles.

## PROBLEMÁTICA

Una instalación fotovoltaica mal planeada en los techos de la universidad:

- genera menos energía de la esperada, por sombras y ángulos inadecuados;
- eleva el costo, porque se compran paneles o inversores que no se aprovechan;
- produce de forma muy irregular a lo largo del año: cae en invierno por la menor altura del sol y en la temporada de lluvias por la nubosidad.

Esto se traduce en una inversión desaprovechada y un menor ahorro en el consumo eléctrico de la universidad.

## NOMBRE LARGO

K'inich: sistema inteligente para la distribución óptima de paneles solares en techos de edificios de la Universidad Politécnica de Chiapas

## NOMBRE CORTO

K'inich

## DESCRIPCIÓN DEL PROYECTO

El proyecto consiste en el desarrollo de un sistema basado en algoritmos genéticos. Toma en cuenta las características del techo, el clima del campus de la UP Chiapas en Suchiapa y la información técnica y económica de los paneles para encontrar la configuración de la instalación fotovoltaica que maximice la energía generada y minimice el costo, las pérdidas por sombra y la variación de la producción entre meses.

- **Estructura del individuo:** un vector real [N, β, γ, d, R].
- **Decodificación:** el vector se convierte en el acomodo de los paneles sobre una rejilla que representa al techo. Ahí se calculan las sombras de los obstáculos y las de una fila de paneles sobre la siguiente.
- **Aptitud:** el producto de los objetivos normalizados. Las minimizaciones entran como inversos con +1 en el denominador, para evitar la división entre cero, y se multiplica por un factor de penalización si se viola alguna restricción:

  f = Ê · 1/(1+Ĉ) · 1/(1+Ŝ) · 1/(1+V̂) · P

El sistema es una aplicación de escritorio. Incluye un editor 2D del techo, visualización 3D de los resultados y catálogos editables de climas, paneles y costos.

## VARIABLES DE DECISIÓN

- N: número de paneles a instalar
- β: inclinación de los paneles (°), entre 5 y 45
- γ: azimut u orientación de los paneles (°), entre 90 y 270
- d: separación libre entre filas de paneles (m), entre 0.6 y 5.0
- R: relación entre la potencia de los paneles y la del inversor (DC/AC), entre 1.0 y 1.5

## VARIABLES A OPTIMIZAR

- E: energía anual generada (kWh)
- C: costo total de la instalación (MXN)
- S: pérdidas de energía por sombra (%)
- V: variación de la producción mensual, medida como coeficiente de variación (σ/μ de la energía mensual)

## OBJETIVOS DE OPTIMIZACIÓN

- Maximizar la energía anual generada (E)
- Minimizar el costo total de la instalación (C)
- Minimizar las pérdidas de energía por sombra (S)
- Minimizar la variación de la producción mensual (V)

## BASE DE CONOCIMIENTO

- Perfil climático del campus de la UP Chiapas en Suchiapa, obtenido de NASA POWER para el punto 16.63° N, 93.09° O. Se usaron 43,824 registros horarios de 2019 a 2023, verificados sin datos faltantes, con irradiancia global (GHI), directa (DNI) y difusa (DHI) y temperatura ambiente. Los registros se convirtieron a la hora local (UTC−6) y se promediaron por mes y hora en un perfil de 12 × 24 = 288 valores. La irradiación global anual promedio es de 1,950 kWh/m². Son estimaciones satelitales regionales, no mediciones en el techo.
- Catálogo de paneles comerciales, tomado de fichas técnicas reales: potencia nominal (W), dimensiones (m), NOCT (°C), coeficiente de temperatura (%/°C), masa (kg) y precio (MXN).
- Costos de estructura e instalación por panel y del inversor por kW, según cotizaciones de distribuidores en México.
- Plano del techo: dimensiones, obstáculos y su altura, medidos en sitio y con Google Earth.
- Capacidad de carga del techo (kg/m²).
- Parámetros fijos del modelo:
  - albedo: 0.2
  - pérdidas por cableado y suciedad: 10 %
  - eficiencia del inversor: 96 %
  - margen de seguridad al borde del techo: 0.6 m

## ENTRADAS AL SISTEMA

- Techo: dimensiones, obstáculos y sus alturas, y tamaño de la celda de la rejilla. Se capturan en el editor gráfico o se importan en CSV.
- Perfil de clima a utilizar: el perfil de 288 valores ya procesado (`clima_2019_2023_288.csv`), otro perfil importado en CSV, o una nueva descarga de NASA POWER con las coordenadas del techo.
- Modelo de panel seleccionado del catálogo.
- Costos unitarios y presupuesto máximo (MXN).
- Capacidad de carga máxima del techo (kg/m²).
- Pesos de los objetivos en la aptitud.
- Parámetros del algoritmo genético:
  - tamaño de la población
  - número de generaciones
  - probabilidad de cruza
  - probabilidad de mutación
  - semilla

## SALIDAS ESPERADAS DEL SISTEMA

- Gráfica de la evolución de la aptitud: el mejor, la media y el peor de cada generación.
- Gráficas de la evolución de cada objetivo (E, C, S, V) del mejor individuo.
- Tabla del mejor individuo de cada generación, con N, β, γ, d, R, E, C, S, V y aptitud, exportable a CSV.
- Los tres mejores individuos, distintos entre sí, mostrando para cada uno:
  - el modelo 3D del techo con los paneles acomodados;
  - el mapa de sombras por mes y hora;
  - una tabla con sus variables de decisión, sus objetivos y su aptitud;
  - una gráfica de la energía producida por mes.
- Comparación de la energía calculada contra PVWatts V8 para una configuración sin obstáculos, y contra una configuración típica de instalador.
- Video resumen del proceso de optimización.
