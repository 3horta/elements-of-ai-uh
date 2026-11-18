# Proyecto 1 — Rover autónomo

*Elementos de Inteligencia Artificial · Ciencia de Datos · Curso 2026-2027*

La exploración autónoma de entornos desconocidos mediante rovers es un área de gran interés en la investigación y el
desarrollo tecnológico.

Tiene aplicaciones en campos como la exploración espacial, la investigación ambiental y la minería, donde operar sin
intervención humana es crucial. Esto permite misiones en lugares inaccesibles o peligrosos para los humanos, aumentando
la seguridad y la eficiencia.

---

## 1. Descripción del problema

Se desea simular un rover autónomo que realice misiones de exploración en un entorno discreto (celdas con obstáculos,
terrenos difíciles, puntos de interés y zonas de comunicación). El rover debe planear, navegar, optimizar y validar sus
acciones bajo limitaciones de recursos (energía, tiempo, comunicación, etc.).

El rover debe explorar un entorno discreto —una rejilla o un grafo—, moverse sobre distintos tipos de superficie
(planos, piedras, rocas, arena fina, dunas), localizar y visitar puntos de interés científicos, y recolectar, analizar y
transmitir datos cumpliendo las restricciones de equipo, tiempo y comunicación establecidas. Además, necesita gestionar
eficientemente sus recursos limitados, como la batería y la memoria, planificar una secuencia de acciones para
maximizar la puntuación de la misión, y optimizar decisiones clave —como el orden de visita de los objetivos, las rutas
y el uso de recursos— utilizando técnicas de inteligencia artificial.

El objetivo es **evaluar el desempeño del rover en misiones y optimizar su funcionamiento** mediante algoritmos de
búsqueda, metaheurísticas y representación simbólica del problema.

**Cada estudiante construye su propio entorno de simulación** y modela el rover con la complejidad necesaria para que
opere efectivamente y el problema resulte interesante desde el punto de vista de la inteligencia artificial.

Lo anterior es el **marco general** del problema: describe el tipo de situación que hay que modelar, no una lista de
requisitos obligatorios. Lo que sí es obligatorio son estas dos advertencias, porque el entorno es donde más tiempo se
pierde:

- **El entorno no es lo que se evalúa.** Debe ser lo más simple que permita que los tres módulos tengan sentido: un
  mapa pequeño, unos pocos tipos de terreno con costos distintos, un puñado de puntos de interés, una o dos zonas de
  comunicación y dos recursos limitados (batería y memoria). Un simulador vistoso con un mal modelado vale menos que uno
  mínimo con un buen modelado.
- **El entorno tiene que ser parametrizable, con un generador de instancias por semilla.** No basta con un mapa fijo: el
  protocolo experimental del punto 3 exige comparar sobre varias instancias, y esas instancias salen de ahí. Conviene
  escribir el generador antes que los algoritmos.

---

## 2. Requisitos técnicos por área de inteligencia artificial

Se implementan **tres módulos**: búsqueda, metaheurísticas y **uno** de los dos apartados de representación simbólica
—planificación o CSP—, a elección de cada estudiante. El apartado no elegido puede abordarse como trabajo adicional,
pero no es obligatorio.

### A) Búsqueda — obligatorio

- Implementar algoritmos de búsqueda para encontrar rutas entre objetivos.
- Las rutas deben considerar costos variables.
- Comparar el rendimiento de distintos algoritmos y heurísticas, siguiendo el protocolo experimental del punto 3.

### B) Planificación — se elige este apartado o el C

- Modelar el problema con acciones, precondiciones y efectos.
- Generar planes de alto nivel que incluyan acciones como moverse, recolectar, analizar, transmitir y recargar.
- Integrar la planificación simbólica con el módulo de búsqueda: el planificador decide la secuencia de alto nivel y
  la búsqueda resuelve cada desplazamiento concreto.

### C) CSP, satisfacción de restricciones — se elige este apartado o el B

- Formular la misión como un problema de satisfacción de restricciones: variables y dominios asociados a qué se hace,
  en qué orden y con qué recursos y tiempos.
- Imponer las restricciones del problema: capacidad de batería y memoria, ventanas de comunicación, precedencias entre
  acciones, límite de tiempo de la misión.
- Resolver el CSP para **construir o validar la secuencia de acciones** del rover, y usar propagación de restricciones
  y heurísticas de selección de variable y valor para hacerlo viable.

*(Quien elija B, planificación, obtiene la secuencia de acciones con el planificador; quien elija C la obtiene o la
valida resolviendo el CSP. No hace falta hacer las dos cosas.)*

### D) Metaheurísticas — obligatorio

- Usar metaheurísticas para ordenar los puntos de interés (POI) a visitar, ajustar parámetros (por ejemplo, el umbral
  de recarga), minimizar el coste total o maximizar la puntuación de la misión, entre otros aspectos relevantes.
- Justificar el uso de metaheurísticas: por qué el problema lo requiere y por qué no basta con una solución exacta.
- Comparar resultados entre algoritmos, siguiendo el protocolo experimental del punto 3.

### E) Sistemas basados en reglas — opcional, bonificable

- Implementar un módulo de reglas para las decisiones del rover: por ejemplo, la política de recarga o la priorización
  de objetivos, con encadenamiento hacia adelante o hacia atrás.
- Se estudia por cuenta propia, con el material de autoestudio de la asignatura.

### Sobre el uso de bibliotecas

**Se pueden usar bibliotecas**, tanto de propósito general (numpy, pandas, networkx, matplotlib) como implementaciones
ya hechas de los algoritmos: solucionadores de CSP, planificadores, bibliotecas de metaheurísticas.

Lo que se evalúa no es haber tecleado el algoritmo, sino **haberlo usado bien**: que el problema esté bien modelado para
esa técnica, que la elección esté justificada, que los parámetros se hayan fijado con criterio y que la comparación
experimental sea seria. Quien use una biblioteca debe poder explicar qué algoritmo hay detrás y por qué lo configuró
así —eso es justamente lo que se pregunta en la defensa.

---

## 3. Protocolo experimental

Toda comparación entre algoritmos o heurísticas tiene que ser experimental y reportarse como tal:

- **Varias instancias** del problema, de tamaños o dificultades distintas, generadas con el generador del entorno.
- **Varias corridas por instancia**, con semillas distintas y declaradas, en los algoritmos con componente aleatoria.
  Los deterministas se corren una vez por instancia, pero se reporta su tiempo igual.
- **Cuántas son suficientes es parte del trabajo**, y hay que justificarlo: si la dispersión entre corridas es grande o
  los resultados cambian mucho de una instancia a otra, hacen falta más. El criterio no es llegar a un número, sino que
  las conclusiones se sostengan con lo que se midió.
- **Presupuesto de cómputo fijo** e igual para todos los algoritmos comparados.
- Reporte de **media y dispersión**, no de la mejor corrida.
- Conclusiones que no excedan lo que muestran los números: si dos algoritmos no se distinguen con la evidencia
  obtenida, hay que decirlo.

Una tabla con un solo número por algoritmo no se acepta.

---

## 4. Qué se entrega

Un **informe de un máximo de 6 páginas**, sin contar los apéndices de figuras y tablas, que incluya:

- Descripción y modelado del problema.
- Implementación del módulo de búsqueda y del de metaheurísticas.
- Implementación del módulo de planificación **o** del de CSP.
- Resultados experimentales y análisis comparativo.
- Discusión de los desafíos encontrados y de cómo se resolvieron.
- Conclusiones y posibles mejoras.

Además, el código fuente documentado, en un repositorio de GitHub que cumpla las reglas de entrega del curso:
estructura clara, entorno declarado (`requirements.txt`, `environment.yml` o `pyproject.toml`), semillas fijadas y un
README que explique cómo ejecutar el proyecto desde cero. **Un resultado que no se puede reproducir no cuenta como
resultado.**

---

## 5. Evaluación

1. **El uso correcto de los algoritmos y técnicas de cada área**: búsqueda, metaheurísticas y el apartado de
   representación simbólica elegido (planificación o CSP). Que estén implementados, que se apliquen al problema y que la
   elección de cada uno esté justificada.
2. La calidad del **modelado** del problema en cada uno de los tres módulos.
3. El **rigor experimental** de las comparaciones (punto 3). Es lo que distingue un trabajo bueno de uno correcto.
4. La **reproducibilidad** del repositorio.
5. La claridad del informe, incluida la discusión honesta de lo que no funcionó.

El apartado E, opcional, bonifica sobre esa nota.

---

## 6. Forma de entrega y defensa

Los proyectos son **individuales**. Las fechas están en la planificación del curso.

El proyecto tiene tres momentos:

- **Revisión de avance.** Se publica en el grupo del curso un reporte breve con el modelo del problema, el entorno
  funcionando y su generador de instancias, qué se resolvió con qué técnica y qué resultados hay hasta el momento. No se
  califica: es la única corrección que se recibe antes de entregar, y se responde con comentarios de la profesora y de
  otro estudiante. Conviene enviar algo real y no una versión maquillada, porque es la oportunidad de corregir el rumbo
  a tiempo.
- **Entrega.** Informe completo, código documentado y resultados experimentales, en el repositorio.
- **Defensa**, en la misma semana de la entrega. Preferiblemente **presencial**: exposición breve del trabajo, con el
  proyecto funcionando, y una ronda de preguntas. Quien no pueda asistir la sustituye por una **videopresentación** en la que discuta lo que hizo y muestre
  el proyecto en ejecución; en ese caso la ronda de preguntas se hace después, una vez revisado el video.

<div class="nota-ia" style="margin-top:2.5em;padding-top:.5em;border-top:1px solid #e3e6eb;font-size:7.5pt;color:#8a8f98;line-height:1.35;">
Nota sobre la elaboración de este texto: elaborado con asistencia de inteligencia artificial, con el modelo de Anthropic Claude Opus 5 (identificador <code>claude-opus-5</code>), en septiembre de 2026, a partir del esquema, las fuentes y las indicaciones de la profesora de la asignatura.
</div>
