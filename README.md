# Elementos de Inteligencia Artificial

Materiales de la asignatura **Elementos de Inteligencia Artificial**, 4.º año de la carrera de Ciencia de Datos.
Curso 2026-2027, modalidad a distancia y asíncrona: las conferencias están escritas para estudiarse por cuenta propia.

## De qué trata

La asignatura tiene dos mitades. La primera cubre los métodos clásicos de la IA: búsqueda en espacios de estados,
satisfacción de restricciones, planificación, modelos gráficos probabilísticos y metaheurísticas. La segunda vuelve
sobre el aprendizaje automático, pero no sobre los algoritmos sino sobre lo que decide si un trabajo sirve: los límites
teóricos de lo que se puede aprender, qué hacer con datos que no son los que el problema necesita, cómo diseñar un
experimento que sostenga una conclusión y qué le pasa a un modelo con el tiempo.

La idea que une las dos mitades: en IA casi nunca hay un algoritmo mejor que todos los demás, sino varias soluciones
defendibles. Elegir entre ellas exige hacer explícitos los criterios, medir con evidencia y asumir qué se sacrifica.

La [guía del curso](guia-del-curso.pdf) explica el funcionamiento, el cronograma y la evaluación.

## Conferencias

Cada conferencia tiene su nota en Markdown (`.md`) y el PDF generado a partir de ella. Los ejercicios están al final
de cada nota, y sus soluciones están en el `.md` dentro de comentarios HTML (`<!-- … -->`), así que no aparecen en
el PDF.

| | Tema | Material |
|---|---|---|
| C1 | Problemas de IA y búsqueda en espacios de estados | [PDF](conferencias/C1%20-%20Busqueda/C1%20-%20Busqueda.pdf) · [nota](conferencias/C1%20-%20Busqueda/Search.md) |
| C2a | Problemas de satisfacción de restricciones | [PDF](conferencias/C2%20-%20CSP%20y%20planificacion/C2a%20-%20CSP.pdf) · [nota](conferencias/C2%20-%20CSP%20y%20planificacion/2a%20-%20CSP.md) |
| C2b | Planificación | [PDF](conferencias/C2%20-%20CSP%20y%20planificacion/C2b%20-%20Planificacion.pdf) · [nota](conferencias/C2%20-%20CSP%20y%20planificacion/2b%20-%20Planificacion.md) |
| C4 | Modelos estadísticos de aprendizaje | [PDF](conferencias/C4%20-%20Modelos%20estadisticos/C4%20-%20Modelos%20estadisticos%20de%20aprendizaje.pdf) · [nota](conferencias/C4%20-%20Modelos%20estadisticos/C4%20-%20Modelos%20estadisticos%20de%20aprendizaje.md) |
| C5 | Límites teóricos: *No Free Lunch* y el patito feo | [PDF](conferencias/C5%20-%20Limites%20teoricos/C5%20-%20No%20free%20lunch%20y%20patito%20feo.pdf) · [nota](conferencias/C5%20-%20Limites%20teoricos/C5%20-%20No%20free%20lunch%20y%20patito%20feo.md) |
| C6 | Datos que no son idóneos | [PDF](conferencias/C6%20-%20Datos%20no%20idoneos/C6.pdf) |
| C7 | Proceso de modelación y evaluación | [PDF](conferencias/C7%20-%20Proceso%20y%20evaluacion/C7%20-%20Proceso%20de%20modelacion%20y%20evaluacion.pdf) · [nota](conferencias/C7%20-%20Proceso%20y%20evaluacion/C7%20-%20Proceso%20de%20modelacion%20y%20evaluacion.md) |
| C8 | Ajuste de hiperparámetros, deriva y aprendizaje online | [PDF](conferencias/C8%20-%20Hiperparametros%20y%20ciclo%20de%20vida/C8%20-%20Ajuste,%20deriva%20y%20aprendizaje%20online.pdf) · [nota](conferencias/C8%20-%20Hiperparametros%20y%20ciclo%20de%20vida/C8%20-%20Ajuste,%20deriva%20y%20aprendizaje%20online.md) |

## Clases prácticas

| | Tema | Material |
|---|---|---|
| CP1 | Modelar el mismo problema de tres maneras | [cp1.pdf](clases-practicas/cp1.pdf) |
| CP2 | Laboratorio: implementar y comparar metaheurísticas | [cp2/](clases-practicas/cp2/) — notebook del laboratorio y una versión resuelta |
| CP3 | Laboratorio: un dataset en malas condiciones | [cp3/](clases-practicas/cp3/) — notebook y datos |
| CP4 | Alta dimensión y revisión crítica de experimentos | [cp4/](clases-practicas/cp4/) — orientación y notebooks |

## Proyectos

- **Proyecto 1 — Rover autónomo**: [enunciado (PDF)](proyectos/Proyecto%201%20-%20Rover.pdf) · código de
  referencia en [proyectos/rover/](proyectos/rover/) (`rover.py`, entorno y rover; `validador.py`, validación de planes).

## Bibliografía

**Básica:** Russell y Norvig, *Artificial Intelligence: A Modern Approach* (4.ª ed., 2020) · Murphy, *Probabilistic
Machine Learning: An Introduction* (2021) · Duda, Hart y Stork, *Pattern Classification* (2.ª ed.).

**Complementaria:** Talbi, *Metaheuristics: From Design to Implementation* · Gendreau y Potvin, *Handbook of
Metaheuristics* · Abu-Mostafa, Magdon-Ismail y Lin, *Learning from Data*.

La lista completa, con editoriales y ediciones, está en [bibliografia.txt](bibliografia.txt).

## Sobre los materiales

Las notas se escriben en Markdown y se convierten a PDF con pandoc. Algunas figuras provienen de los libros de la
bibliografía, con su atribución en el pie. Los materiales se elaboraron con asistencia de inteligencia artificial
(modelos Claude, de Anthropic), a partir del esquema, las fuentes y las indicaciones de la profesora. Cada documento
lo indica al final.
