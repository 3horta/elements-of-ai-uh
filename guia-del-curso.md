# Elementos de Inteligencia Artificial
## Guía del curso — Ciencia de Datos, curso 2026-2027, modalidad a distancia

---

## De qué va esta asignatura

Esta es la asignatura de cierre de la disciplina de Inteligencia Artificial, y tiene dos mitades.

En la **primera mitad** verán los métodos clásicos de la IA: búsqueda en espacios de estados, satisfacción de
restricciones, planificación, modelos gráficos probabilísticos y metaheurísticas. Son los métodos con los que se atacan
problemas donde el espacio de soluciones es enorme y no existe una fórmula que dé la respuesta, y las herramientas para
razonar cuando además hay incertidumbre. No los han visto en ninguna otra asignatura de la carrera.

En la **segunda mitad** volverán sobre el aprendizaje automático, pero no sobre los algoritmos,
sino sobre lo que rodea a los algoritmos y decide si un trabajo sirve o no sirve: los límites teóricos de lo que se
puede aprender, qué hacer cuando los datos no son los que el problema necesita, cómo se diseña un experimento que
permita sostener una conclusión, y qué le pasa a un modelo cuando lleva dos años desplegado.

Las dos mitades sostienen la misma tesis, que es la idea central del curso:

> En Inteligencia Artificial casi nunca hay una solución óptima ni un algoritmo mejor que todos los demás. Lo que
> suele haber son **varias soluciones defendibles**, cada una mejor en unos aspectos y peor en otros: más exacta pero
> más cara, más rápida pero menos robusta, más precisa pero imposible de explicarle a quien tiene que usarla. Muchas
> veces ni siquiera son comparables entre sí mientras no se diga **con qué criterios** se las compara, y esos criterios
> los pone el problema, no la técnica. Elegir es entonces hacer explícitos los criterios, medir con evidencia y asumir
> qué se sacrifica. Conducir esa elección, y comunicar qué queda fuera del alcance de lo que uno construyó, es parte
> del oficio del científico de datos.

Al terminar el curso deben ser capaces de situar un problema nuevo en un marco conocido, decidir qué técnica tiene
sentido y por qué, trabajar con datos que llegan en malas condiciones, y defender con evidencia qué puede y qué no puede
afirmar su solución, incluido reconocer cuándo dos alternativas son, con la evidencia disponible, igual de defendibles.

---

## Cómo funciona el curso

El curso es fundamentalmente a distancia y asíncrono: no hay clases en vivo. Las conferencias se les envían para que
las estudien, y el grupo del curso es el principal espacio de intercambio: ahí se responden las preguntas que se
proponen con cada tema, se plantean dudas y se discuten ideas.

El curso dura **10 semanas** y se publican **15 unidades** de contenido —8 conferencias, 5 clases prácticas y el
seminario final— a razón de una en las semanas impares y dos en las pares. La conferencia sobre datos es la más larga
del curso y por eso va en dos notas.

El material del curso son las notas de clase y la bibliografía recomendada.

Además, estaremos enviando:

| | Qué es |
|---|---|
| **Cuestionario** | Preguntas de autoevaluación|
| **Consigna de debate** | Una o dos preguntas abiertas que se discuten en el grupo, con una ventana de días para responder |

### Cuando llega una consigna de debate, se responde

Son ocasionales, pero no son opcionales: sustituyen a la discusión en el aula, y son donde se practica la mitad de lo
que esta asignatura quiere enseñarles, que es argumentar una decisión y sostenerla frente a alguien que no está de
acuerdo.

**La regla es concreta: cada quien publica una respuesta propia y un comentario a la respuesta de otro compañero**,
dentro de la ventana de discusión. Vale más una respuesta que se moja y se equivoca que tres que repiten lo que dice la
nota. Al cerrar cada hilo, podremos elegir las mejores respuestas y aprender de los errores más frecuentes.

Entre una consigna y otra el grupo sigue abierto, y esa es la idea: para dudas, para lo que no se entendió de una nota,
y para lo que quieran plantear ustedes.

### Cómo funcionan las clases prácticas

Cada clase práctica ocupa una semana y sigue siempre la misma secuencia:

1. Se publica el enunciado y el notebook, con el plazo.
2. Trabajan. El hilo de dudas queda abierto todo el tiempo.
3. **Publican sus resultados en el grupo.** No es una evaluación: es el material de la discusión, así que lo que
   publiquen tiene que contener realmente sus ideas, como si estuvieran en un aula y tuvieran que explicarle a un
   compañero qué hicieron y por qué. No se trata de publicar la versión final ni un resultado perfecto, sino lo que
   hicieron y cómo lo hicieron, para que otros puedan comentarlo y ustedes puedan aprender de los comentarios.
4. Se discute en el grupo, con comentarios de las profesoras y de los compañeros.
5. Se publica una solución comentada y se cierra con la entrega.

**Las dudas van en el grupo**, para que sirva de espacio de intercambio y aprendizaje. Lo que sea personal, por mensaje
privado.


---

## Cronograma

(C = conferencia, CP = clase práctica.)

| Semana | Se publica | Qué se espera de ustedes | Entregas |
|---|---|---|---|
| **1** | C1 — Problemas de IA y búsqueda en espacios de estados. Orientación del **Proyecto 1** (individual). | Estudiar la nota de C1 | Consigna de apertura: formular un problema propio como problema de búsqueda |
| **2** | C2 — Restricciones y planificación (notas 2a y 2b) · CP1: modelar de tres maneras | Estudiar las dos notas de C2, y resolver los ejercicios de la CP1 y publicar sus resultados en el grupo | — |
| **3** | C3 — Metaheurísticas | Estudiar la nota de C3 | — |
| **4** | C4 — Modelos estadísticos de aprendizaje · CP2 — Laboratorio de metaheurísticas | Estudiar la nota de C4, e implementar dos metaheurísticas y publicar los resultados en el grupo | **Revisión de avance del Proyecto 1** |
| **5** | C5 — Límites teóricos: no free lunch y el patito feo | Estudiar la nota de C5 y responder la consigna de debate | **Entrega CP2**. Autoestudio de sistemas expertos |
| **6** | C6 — Datos que no son idóneos (notas 6a y 6b) | Estudiar las dos notas de C6 | **Entrega y defensa del Proyecto 1** |
| **7** | CP3 — Laboratorio: trabajo con datos | Trabajar sobre el propio dataset y publicar el diagnóstico en el grupo | — |
| **8** | C7 — Proceso de modelación y evaluación · CP4 — Alta dimensión y revisión crítica | Estudiar la nota de C7 y resolver la CP4 | **Entrega CP3**: preparación de datos del Proyecto 2 |
| **9** | C8 — Ajuste de hiperparámetros, deriva y aprendizaje online | Estudiar la nota de C8 y preparar la presentación del seminario | **Entrega CP4**: diseño experimental del Proyecto 2 |
| **10** | CP5 · **Seminario del Proyecto 2** | Publicar el diseño de su experimento y comentar el de dos compañeros | **Entrega CP5**: ajuste, límites y ciclo de vida del Proyecto 2 |
| **Cierre** | Defensa del Proyecto 2 | Ver más abajo las dos variantes de defensa | **Entrega final del informe y el repositorio del Proyecto 2** |


---

## Los dos proyectos

El curso se articula alrededor de dos trabajos: un proyecto de IA clásica en la primera mitad y, en la segunda, un
estudio experimental de menor escala que se construye por partes y se presenta en un seminario.

### Proyecto 1 — Rover autónomo (individual)

Simular un rover que explora un entorno discreto con recursos limitados, y resolver con técnicas de IA clásica los
problemas que aparecen. Son **tres módulos**: rutas entre objetivos (**búsqueda**), orden de visita y ajuste de umbrales
(**metaheurísticas**) y **uno** de los dos apartados de representación simbólica, a elección: secuencia de acciones con
precondiciones y efectos (**planificación**) o validación de recursos y tiempos (**CSP**).

Un requisito que conviene leer desde ahora: **la comparación entre algoritmos y heurísticas tiene que ser
experimental** —varias instancias, varias corridas con semillas distintas, presupuesto de cómputo fijo, y reporte de
media y dispersión, no de la mejor corrida. Una tabla con un solo número por algoritmo no se acepta.

Hay un apartado **bonificable** opcional: un módulo de reglas para las decisiones del rover (política de recarga,
priorización de objetivos), con material de autoestudio sobre sistemas basados en reglas.

En la semana 4 hay una **revisión de avance**: cada quien reporta su modelo del problema, qué resolvió con qué técnica
y qué resultados tiene hasta el momento —a esa altura, lo que se apoya en las tres primeras conferencias. Recibe
comentarios de la profesora y de otros estudiantes. No es evaluación de la entrega final; es la única corrección que
reciben antes de entregar, así que conviene enviar algo real y no una versión maquillada.

### Proyecto 2 — Estudio experimental (individual)

Un estudio sobre un problema real de aprendizaje, en un dominio que cada quien elige y reserva —dominios distintos por
estudiante, por orden de llegada.

**Lo que se califica no es cuántos modelos entrenaron, sino si el estudio permite sostener sus conclusiones.** Un
trabajo con dos modelos, un baseline honesto, una métrica justificada y una medida de variabilidad vale más que uno con
ocho modelos y una tabla sin protocolo.

Se construye por partes, con las entregas de las clases prácticas:

1. **Preparación de datos** (CP3 en la semana 7, entrega en la 8): diagnóstico de calidad, mecanismo de los datos
   faltantes y estrategia elegida, ruido y atípicos, pipeline sin fuga de información.
2. **Diseño experimental** (CP4 en la semana 8, entrega en la 9): preguntas, baseline, esquema de partición, métricas y
   su justificación en términos del costo real del error.
3. **Ajuste, límites y ciclo de vida** (CP5 en la semana 10): ajuste de hiperparámetros dentro de la validación,
   comparación de modelos con medida de variabilidad, y qué le pasaría al modelo con el tiempo.
4. **Informe final** (máx. 5 páginas) + repositorio reproducible, al cierre del curso.

En la semana 10 está el **seminario**: cada estudiante publica el diseño de su experimento y **qué le permite y qué no
le permite concluir**, y comenta el de los compañeros.

---

## Reglas de entrega

- **Todo se entrega por repositorio git**, con una estructura clara (`src/`, `data/`, `notebooks/`, `outputs/`), el
  entorno declarado (`requirements.txt`, `environment.yml` o `pyproject.toml`) y **las semillas fijadas**. Un resultado
  que no se puede reproducir no cuenta como resultado.
- Esto vale también para los algoritmos de IA clásica: se entrega **código que corre y tablas de resultados**, no
  pseudocódigo. Es lo que hace posible el requisito de comparar con varias corridas y reportar dispersión.
- Los dominios del Proyecto 2 son **únicos por estudiante** y se reservan por mensaje privado a la profesora, por orden
  de llegada.

---

## Evaluación

La evaluación es continua y se basa en la participación en las consignas de debate y las clases prácticas y los dos proyectos.

### Las defensas

Hay **dos variantes**, y los detalles se precisarán más adelante:

- **Presencial, que es la recomendada.** Exposición breve y una ronda de preguntas.
- **Videopresentación enviada**: graban una presentación discutiendo lo que hicieron y mostrando el proyecto
  funcionando. En esta variante la ronda de preguntas se hace después, una vez revisado el video.


### Sobre el uso de asistentes de IA

Se declara en el informe qué se usó y para qué. No está prohibido, pero **en la defensa hay preguntas sobre el trabajo
propio**: lo que se evalúa es la capacidad de fundamentar cada decisión que aparece en la entrega. Si no pueden explicar
por qué eligieron esa métrica, esa imputación o esa heurística, la entrega no se sostiene, sin importar quién la
escribió.

---

## Bibliografía

**Básica**
1. Russell, S. y Norvig, P. *Artificial Intelligence: A Modern Approach*, 4.ª edición, 2020.
2. Murphy, K. P. *Probabilistic Machine Learning: An Introduction*, MIT Press, 2021.
3. Duda, R. O. et al. *Pattern Classification*, 2.ª edición.

**Complementaria**
- Talbi, E.-G. *Metaheuristics: From Design to Implementation*.
- Gendreau, M. y Potvin, J.-Y. *Handbook of Metaheuristics*.
- Abu-Mostafa, Y., Magdon-Ismail, M. y Lin, H.-T. *Learning from Data*.

<div class="nota-ia" style="margin-top:2.5em;padding-top:.5em;border-top:1px solid #e3e6eb;font-size:7.5pt;color:#8a8f98;line-height:1.35;">
Nota sobre la elaboración de este texto: elaborado con asistencia de inteligencia artificial, con el modelo de Anthropic Claude Opus 5 (identificador <code>claude-opus-5</code>), en septiembre de 2026, a partir del esquema, las fuentes y las indicaciones de la profesora de la asignatura.
</div>
