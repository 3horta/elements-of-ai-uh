<style>
/* Estilo propio de la C8 (el mismo de la C7): se suma al estilo común del curso (_pdf/estilo.html) */
h1 { font-size: 22pt; color: #14365e; }
h2 { color: #14365e; border-bottom: 2px solid #2a78d6; break-before: auto; }
h3 { color: #1f4f86; }
blockquote { border-left: 4px solid #2a78d6; background: #f1f6fd; color: #1a1a1a; border-radius: 0 4px 4px 0;
             break-inside: auto; }
blockquote strong:first-child { color: #14365e; }
pre { background: #fff8f1; border: 1px solid #f3d3b5; border-left: 4px solid #e07b2a; border-radius: 4px;
      padding: 8px 10px; font-size: 8.6pt; line-height: 1.4; white-space: pre-wrap; break-inside: avoid;
      -webkit-print-color-adjust: exact; print-color-adjust: exact; }
pre code { background: none; padding: 0; font-size: 8.6pt; }
table { font-size: 8.6pt; }
th { background: #e8eef7; color: #14365e; }
tbody tr:nth-child(even) td { background: #fafbfc; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
figure { margin: 1.2em 0 1.4em; }
figure img { max-height: 8.5cm; }
figcaption { border-top: 1px solid #e3e6eb; padding-top: .35em; }
.nota-ia { margin-top: 2.5em; padding-top: .5em; border-top: 1px solid #e3e6eb; font-size: 7.5pt; color: #8a8f98;
           line-height: 1.35; }
</style>

# C8 — Ajuste de hiperparámetros y el modelo en el tiempo

*Elementos de Inteligencia Artificial · Ciencia de Datos · Curso 2026-2027*

---

Hoy vamos a trabajar con un ejemplo nuevo: un detector de fraude con tarjetas. Supongamos que ya lo evaluamos con
lo que vimos en la C7: validación cruzada estratificada, una métrica elegida según lo que cuesta cada error y
comparaciones pareadas con su variabilidad. Aun así nos quedan dos problemas.

El primero es que el modelo, un *gradient boosting*, lo entrenamos con los hiperparámetros que trae la biblioteca por
defecto. ¿Cuántos árboles? ¿Qué profundidad? ¿Qué tasa de aprendizaje? Esos valores los eligió alguien pensando en
un problema promedio, no en el nuestro, así que lo más probable es que haya una configuración mejor. **¿Cómo la
buscamos?**

El segundo es más incómodo. Imaginen que encontramos esa configuración, la evaluamos con cuidado y ponemos el
detector en producción con una sensibilidad estimada del 85 %. Seis meses después, el banco se da cuenta de que cada
vez se le escapan más fraudes. El modelo es el mismo; lo que cambió fueron los estafadores, que aprendieron qué
transacciones se bloquean y cambiaron su forma de operar. Todo lo que hicimos en la C7 suponía que los datos del
futuro se parecen a los de entrenamiento, y aquí eso dejó de ser cierto. **¿Qué hacemos entonces?**

El primer problema lo vamos a tratar como un problema de búsqueda. El segundo nos obliga a pensar en el modelo como
algo que vive en el tiempo.

> **Objetivos de esta nota.** Al terminarla deberían poder:
>
> 1. formular el ajuste de hiperparámetros como un problema de búsqueda;
> 2. elegir una estrategia de ajuste según el presupuesto y la naturaleza del espacio, y explicar por qué la búsqueda
>    aleatoria suele ganarle a la rejilla;
> 3. situar el ajuste dentro del protocolo de evaluación y reconocer cuándo una estimación está contaminada;
> 4. distinguir los tipos de deriva y proponer cómo monitorear un modelo desplegado y cuándo reentrenarlo;
> 5. describir el aprendizaje online, sus ventajas y sus riesgos, y decidir cuándo conviene;
> 6. escribir los límites de una solución de forma concreta y verificable.

---

## 1. El ajuste de hiperparámetros es un problema de búsqueda

### Parámetros e hiperparámetros

Empecemos por separar dos cosas. Los **parámetros** son lo que el algoritmo aprende de los datos: los pesos de una
regresión logística, los umbrales de corte de cada árbol. Los **hiperparámetros** los decidimos nosotros **antes**
de entrenar, porque el algoritmo no puede aprenderlos solo: cuántos árboles, qué profundidad máxima, cuánta
regularización. Si pensamos el aprendizaje como una búsqueda en el espacio de hipótesis, como en la C4, los
hiperparámetros dicen **dónde** y **cómo** se busca.

No todos son del mismo tipo, y eso va a pesar a la hora de elegir cómo ajustarlos:

- **continuos**, como la tasa de aprendizaje o la constante de regularización. Con estos casi siempre conviene
  trabajar en escala logarítmica, porque pasar de 0,001 a 0,01 cambia tanto como pasar de 0,1 a 1;
- **enteros**, como el número de árboles o la profundidad máxima;
- **categóricos**, como el criterio de división o el tipo de núcleo de una SVM;
- **condicionales**, que solo existen según el valor de otro: el `gamma` de una SVM solo tiene sentido si el núcleo
  es gaussiano.

### La formulación

Escribámoslo de manera formal. Llamemos $\mathcal{A}_\lambda$ al algoritmo de aprendizaje configurado con el vector
de hiperparámetros $\lambda$, que toma valores en un espacio $\Lambda$. Ajustar es resolver

$$\lambda^* = \arg\min_{\lambda \in \Lambda} \; \hat{E}_{\text{val}}(\mathcal{A}_\lambda, D),$$

donde $\hat{E}_{\text{val}}$ es el error estimado por validación (por ejemplo, el promedio sobre los folds de una
validación cruzada) del modelo que aprende $\mathcal{A}_\lambda$ con los datos $D$.

¿Qué tipo de función es esta? Para evaluarla en **un solo punto** hay que entrenar el modelo una vez por fold, y en
nuestro detector eso puede tardar minutos. Además tiene **ruido**: si cambiamos la partición o la semilla, el valor
cambia (lo vimos en la C7, sección 3). Tampoco tenemos **gradiente**, no hay una fórmula que nos diga hacia dónde
movernos para mejorar. Y para colmo, el espacio mezcla variables continuas, enteras y categóricas. En resumen, es una
caja negra, cara de evaluar y con ruido.

### Relación con el ajuste de metaheurísticas

Este problema no es del todo nuevo para ustedes. En la C3 ajustamos los parámetros de las metaheurísticas, y allí
corríamos cada configuración sobre varias instancias y con varias semillas. Si ponemos los dos problemas lado a lado:

| Ajustar una metaheurística (C3) | Ajustar un modelo (C8) |
|---|---|
| Parámetros: tamaño de la lista tabú, temperatura inicial, probabilidad de mutación | Hiperparámetros: número de árboles, profundidad, tasa de aprendizaje |
| Evaluar una configuración = correr la metaheurística | Evaluar una configuración = entrenar y validar el modelo |
| Sobre varias **instancias** del problema | Sobre varios **folds** de los datos |
| Con varias **semillas**, porque el algoritmo es estocástico | Con varias **particiones**, porque la estimación es ruidosa |
| Instancias de ajuste separadas de las de evaluación | Datos de ajuste separados de los de prueba (sección 3) |
| No existe una configuración óptima para todos los problemas | No existe una configuración óptima para todos los conjuntos de datos (C5) |

La última fila es el *No Free Lunch* de la C5, ahora aplicado a los hiperparámetros. Los valores por defecto de una
biblioteca son un compromiso razonable para un problema promedio, pero ninguno de nosotros trabaja con el problema
promedio.

Talbi le llama a esto **meta-optimización**: un problema de optimización en el que cada "solución" es un vector de
parámetros y la función objetivo es el rendimiento de otro algoritmo. Se puede resolver con cualquier método de
búsqueda, incluso con una metaheurística, y entonces tenemos una búsqueda ajustando a otra búsqueda.

### Ajuste off-line y control on-line

Los hiperparámetros se pueden fijar de dos maneras:

- En el **ajuste off-line** se eligen **antes** de entrenar y no cambian mientras el modelo aprende. Es el problema
  de la fórmula de arriba, y de eso trata la sección 2.
- En el **control on-line** se van adaptando **durante** el entrenamiento, según cómo vaya. El ejemplo más conocido
  es la tasa de aprendizaje de una red: empieza grande y se va reduciendo según una programación (*learning rate
  schedule*), o se adapta sola, como en Adam. La parada temprana (*early stopping*) también entra aquí, porque el
  número de épocas se decide mientras se entrena, mirando el error de validación.

Al control on-line volvemos en la sección 5, porque en el aprendizaje online la tasa de aprendizaje es uno de los
problemas principales.

> **Para ampliar.** Russell y Norvig, sección 19.4.4 (*Hyperparameter tuning*). Talbi, sección 1.6, pp. 54–57: ajuste
> off-line y on-line, y la meta-optimización con su figura 1.25. *Handbook of Metaheuristics*, capítulo 17 (Stützle y
> López-Ibáñez), sección 17.2.2: la definición formal del problema de configuración.

---

## 2. Estrategias de ajuste

### Diseñar el experimento

Antes de pensar en cómo buscar, hay que decidir dónde. En diseño de experimentos, a cada hiperparámetro se le llama
**factor** y a cada valor que vamos a probar, **nivel**. Elegir los rangos y las escalas es una decisión de
modelación importante: si el valor bueno no está dentro del espacio, ninguna estrategia lo va a encontrar.

Lo más completo sería el **factorial completo**, o sea, probar todas las combinaciones. Con $n$ factores de $k$
niveles cada uno salen $k^n$ configuraciones. Hagamos la cuenta para el detector: cuatro hiperparámetros (número de
árboles, profundidad, tasa de aprendizaje y tamaño mínimo de las hojas) con cinco niveles cada uno dan $5^4 = 625$
configuraciones. Con validación cruzada de 5 folds son $3125$ entrenamientos, y si cada uno tarda dos minutos, más
de cuatro días de cómputo. Y eso sin repetir nada con otras semillas.

En el otro extremo está variar un factor por vez y dejar los demás fijos. Es mucho más barato, pero supone que cada
hiperparámetro afecta al modelo por su cuenta, y eso casi nunca es así. En un *gradient boosting*, por ejemplo, la
tasa de aprendizaje y el número de árboles se compensan: con una tasa pequeña hacen falta muchos árboles. El mejor
valor de uno depende del otro, y variando de uno en uno no vemos esas **interacciones**.

Entre esos dos extremos hay diseños que prueban solo una parte de las combinaciones, pero escogida con cuidado.
Veamos dos.

El **factorial fraccionado** escoge las combinaciones de manera que queden **equilibradas**: cada valor de cada
hiperparámetro aparece el mismo número de veces, y cada pareja de valores de dos hiperparámetros también. Pongamos
tres hiperparámetros con dos niveles cada uno. El factorial completo tendría $2^3 = 8$ combinaciones, pero con estas
cuatro alcanza:

| Corrida | Profundidad | Tasa de aprendizaje | Número de árboles |
|---|---|---|---|
| 1 | 3 | 0,01 | 500 |
| 2 | 8 | 0,01 | 100 |
| 3 | 3 | 0,1 | 100 |
| 4 | 8 | 0,1 | 500 |

Tomen dos columnas cualesquiera y van a encontrar las cuatro parejas posibles, cada una una sola vez. La tasa 0,01,
por ejemplo, se prueba con 100 y con 500 árboles, y la tasa 0,1 también. Así, con la mitad de las corridas, podemos
estimar el efecto de cada hiperparámetro y ver cómo se combinan de dos en dos. Lo que se paga es que algunos efectos
quedan mezclados: con esta tabla no hay forma de separar el efecto del número de árboles de la interacción entre
profundidad y tasa.

El **hipercubo latino** se usa con hiperparámetros continuos. Si vamos a hacer $m$ corridas, dividimos el rango de
cada hiperparámetro en $m$ intervalos iguales y tomamos un valor dentro de cada uno, de modo que **cada intervalo de
cada hiperparámetro se use exactamente una vez**. Después emparejamos esos valores al azar entre hiperparámetros.
Con dos hiperparámetros y $m = 5$, el plano queda como una cuadrícula de $5 \times 5$, y las cinco muestras quedan
como cinco torres en un tablero de ajedrez que no se atacan: ninguna comparte fila ni columna. Con solo cinco
corridas probamos cinco valores distintos de cada hiperparámetro, repartidos por todo su rango.

> **Para ampliar.** Talbi, sección 1.6.1, pp. 55–56: factores, niveles, diseño factorial y sus alternativas.

### Rejilla frente a búsqueda aleatoria

La **búsqueda en rejilla** (*grid search*) es el factorial completo aplicado a los hiperparámetros: para cada uno
fijamos una lista de valores y probamos todas las combinaciones. La **búsqueda aleatoria** (*random search*) sortea
configuraciones del espacio, cada hiperparámetro según alguna distribución, y prueba tantas como permita el
presupuesto.

Uno pensaría que la rejilla tiene que ganar, porque es más sistemática. Pues casi nunca gana. La razón es que, en la
mayoría de los problemas, **solo unos pocos hiperparámetros importan de verdad**, y no sabemos de antemano cuáles son.
Miren la figura 1: hay dos hiperparámetros, uno que importa mucho y otro que casi no influye, y los dos métodos tienen
el mismo presupuesto de nueve corridas.

![**Figura 1.** Rejilla y búsqueda aleatoria con el mismo presupuesto. La curva naranja de arriba muestra cómo cambia el rendimiento con el hiperparámetro importante; la franja gris de la derecha, que el otro casi no influye. La rejilla gasta sus nueve corridas en solo tres valores del hiperparámetro que importa y en esta ilustración no se acerca al máximo. La búsqueda aleatoria prueba nueve valores distintos. Elaboración propia, inspirada en Bergstra y Bengio (2012).](resources/c8_rejilla_aleatoria.png)

La rejilla prueba tres veces cada valor del hiperparámetro importante, y en esas repeticiones lo único que cambia es
el que no importa. Son corridas que se pierden. La búsqueda aleatoria, en cambio, nunca repite un valor.

Hay también un argumento de probabilidad, y no depende de cuántos hiperparámetros haya. Supongamos que nos
conformamos con una configuración que esté entre el 5 % mejor del espacio. Cada sorteo cae ahí con probabilidad
$p = 0{,}05$, así que la probabilidad de que al menos uno de $n$ sorteos caiga ahí es

$$1 - (1-p)^n, \qquad 1 - 0{,}95^{60} \approx 0{,}95.$$

Es decir, con **60 corridas** al azar tenemos un 95 % de probabilidad de encontrar una configuración del 5 % mejor,
ya sean dos hiperparámetros o veinte. La rejilla no nos da ninguna garantía parecida.

> **Para ampliar.** Russell y Norvig, sección 19.4.4 (*grid search* y *random search*). Bergstra y Bengio (2012),
> *(externa)*: el artículo que mostró este argumento con experimentos.

### Optimización bayesiana

La rejilla y la búsqueda aleatoria tienen algo en común: **no aprenden de lo que ya probaron**. La corrida 50 se
elige igual que la primera. Si cada evaluación cuesta minutos u horas, estamos tirando información. La
**optimización bayesiana** usa todo lo evaluado hasta el momento para decidir qué probar después, y para eso necesita
dos piezas:

1. Un **modelo sustituto** (*surrogate*) de la función objetivo. Es un modelo barato que, a partir de los pares
   (configuración, error) que ya tenemos, predice el error de una configuración nueva **y también cuánta
   incertidumbre tiene esa predicción**. El más usado es un proceso gaussiano, aunque también se usan bosques
   aleatorios (como en SMAC) y estimadores de densidad (TPE).
2. Una **función de adquisición**, que mira esas predicciones y decide qué configuración conviene probar ahora. Las
   más comunes son la mejora esperada (*expected improvement*) y la cota superior de confianza (UCB).

La función de adquisición es la que reparte entre **explotar**, o sea, probar cerca de lo que ya funcionó, y
**explorar**, probar donde el sustituto está muy inseguro, por si ahí hay algo mejor.

¿Cuál es el problema? El propio sustituto tiene un costo, y además es difícil paralelizar: como cada punto depende de
los anteriores, no se pueden lanzar muchas evaluaciones a la vez así como así.

> **Para ampliar.** Russell y Norvig, sección 19.4.4 (*Bayesian optimization*). Murphy, sección 17.2 (procesos
> gaussianos, el sustituto más común). *Handbook of Metaheuristics*, sección 17.2.3.2 (SMAC, optimización basada en
> modelos aplicada a configurar algoritmos).

### Descartar pronto las configuraciones malas

Otra manera de ahorrar es no gastar lo mismo en todas las configuraciones. Muchas se ven malas desde el principio, y
no hace falta entrenarlas completas para darse cuenta. Esa es la idea de los algoritmos de **carreras** (*racing*):
se evalúan todas las candidatas con poco presupuesto (pocos folds, o una parte de los datos), se eliminan las que son
estadísticamente peores y se sigue evaluando solo a las que quedan.

En aprendizaje, la versión más conocida es la **reducción sucesiva a la mitad** (*successive halving*). Lo que se va
repartiendo puede ser el número de árboles, las épocas de entrenamiento o la fracción de los datos.

```text
SUCCESSIVE-HALVING(configuraciones C, presupuesto inicial b, factor η)
    mientras C tenga más de una configuración:
        para cada c en C:
            entrenar c con presupuesto b y medir su error de validación
        C ← el mejor 1/η de C              # nos quedamos con las mejores
        b ← η · b                          # y les damos más presupuesto
    devolver la configuración que queda
```

Veamos un ejemplo con 27 configuraciones y $\eta = 3$. En la primera ronda entrenamos las 27 con presupuesto $b$,
digamos 50 árboles. Pasan 9, que reciben $3b$; después pasan 3 con $9b$, y al final queda una con $27b$. En total
gastamos $27b + 27b + 27b + 27b = 108\,b$, mientras que entrenar las 27 completas costaría $27 \times 27b = 729\,b$.
Casi siete veces menos.

Ahora, hay un riesgo, y seguramente ya lo están viendo: una configuración que **arranca lento** pero que al final
sería la mejor (por ejemplo, una con tasa de aprendizaje pequeña) puede quedar fuera en las primeras rondas.
**Hyperband** trata de atenuarlo: corre *successive halving* varias veces, cada vez con un compromiso distinto entre
cuántas configuraciones se prueban y cuánto presupuesto recibe cada una.

> **Para ampliar.** *Handbook of Metaheuristics*, sección 17.2.3 (F-race e irace). Li et al. (2018), *(externa)*:
> el artículo de Hyperband, que incluye *successive halving*. La bibliografía del curso no trata estos dos métodos.

### Ajustar con metaheurísticas

El espacio de configuraciones también se puede recorrer con metaheurísticas. Algunos ejemplos:

- **ParamILS** hace búsqueda local iterada sobre las configuraciones: cambia un parámetro a la vez, se queda con el
  cambio si mejora y usa perturbaciones para salir de los óptimos locales.
- **Los algoritmos genéticos** codifican cada configuración como un cromosoma y la hacen evolucionar.
- **El entrenamiento basado en poblaciones** (*population-based training*, PBT) entrena en paralelo una población de
  modelos con hiperparámetros distintos. Cada cierto tiempo, los peores copian los pesos y los hiperparámetros de los
  mejores y los mutan un poco. Russell y Norvig lo presentan directamente como un algoritmo genético. Como los
  hiperparámetros cambian mientras se entrena, PBT mezcla el ajuste off-line con el control on-line.

> **Para ampliar.** Russell y Norvig, sección 19.4.4 (*population-based training*). *Handbook of Metaheuristics*,
> sección 17.2.3.1 (ParamILS). Talbi, sección 1.6.1 (meta-optimización con una metaheurística).

### AutoML

Se puede ir un paso más allá y no fijar ni siquiera el algoritmo: buscar a la vez **qué** modelo usar y **con qué**
hiperparámetros. A ese problema se le llama CASH (*combined algorithm selection and hyperparameter optimization*), y
es lo que está detrás de los sistemas de **AutoML**, como Auto-WEKA o auto-sklearn. Es un espacio condicional típico:
si se elige una SVM aparecen sus hiperparámetros, y si se elige un bosque aparecen otros. La búsqueda de
arquitecturas neuronales (*neural architecture search*) es el mismo problema, pero con redes.

Eso sí, hay cosas que AutoML **no** hace por nosotros: decidir qué pregunta le hacemos a los datos, escoger una
métrica que refleje lo que cuesta cada error y armar una partición que imite el uso. Todo eso lo vimos en la C7, y si
está mal hecho, AutoML va a optimizar muy bien algo que no es lo que necesitamos.

> **Para ampliar.** *Handbook of Metaheuristics*, sección 17.5.2 (selección de algoritmos y portafolios). Murphy,
> sección 14.3.6 (búsqueda de arquitecturas neuronales). Hutter, Kotthoff y Vanschoren (2019), capítulo 1,
> *(externa)*: una revisión completa de la optimización de hiperparámetros.

### Resumen

| Estrategia | ¿Aprende de lo ya probado? | ¿Se paraleliza bien? | Cuándo conviene |
|---|---|---|---|
| Rejilla | No | Sí | Uno o dos hiperparámetros con pocos valores |
| Búsqueda aleatoria | No | Sí | Punto de partida razonable casi siempre; buena referencia |
| Optimización bayesiana | Sí | Con dificultad | Evaluaciones muy caras y espacio de dimensión moderada |
| *Successive halving* / Hyperband | Solo descarta | Sí | Hay un recurso que se puede escalar (árboles, épocas, datos) |
| Metaheurísticas / PBT | Sí | Sí (las poblacionales) | Espacios grandes, mixtos o condicionales; redes con PBT |

Un consejo práctico: antes de cualquier método sofisticado, corran una búsqueda aleatoria con el mismo presupuesto.
Si el método que eligieron no la supera con claridad, no vale la pena complicarse. Es la misma idea del baseline de
la C7, ahora para el ajuste.

---

## 3. El ajuste dentro del protocolo

Ajustar hiperparámetros es, al final, **elegir entre candidatos**: probamos muchas configuraciones y nos quedamos con
la mejor. En la C7 (sección 4) vimos lo que pasa si reportamos el puntaje de validación del candidato elegido: sale
optimista, porque es el mejor de muchas estimaciones con ruido. Para evitarlo usamos la **validación cruzada
anidada**. En el bucle interno se ajustan los hiperparámetros, y en el externo se mide qué tan bien funciona todo ese
proceso, con datos que no se usaron para elegir. Lo que cambia ahora es la escala: en la C7 comparábamos unos pocos
modelos, y al ajustar hiperparámetros podemos probar cientos o miles de configuraciones.

En la C5 le pusimos número a ese optimismo: si elegimos entre $M$ configuraciones, la cota de Hoeffding se multiplica
por $M$, y una búsqueda de 500 configuraciones es un $M = 500$. **Mientras más buscamos, más optimista sale el mejor
puntaje de validación**, y más importante es que la evaluación final se haga con datos que la búsqueda no vio. Una
búsqueda muy agresiva puede terminar sobreajustando el conjunto de validación, igual que un árbol muy profundo
sobreajusta el de entrenamiento.

Hay tres fugas que aparecen mucho, y las tres son formas de espionaje de datos (*data snooping*):

- **Preprocesar fuera del bucle.** Estandarizar, imputar o seleccionar características (C6) con todos los datos y
  después ajustar. Todo lo que se aprende de los datos tiene que ir dentro del fold.
- **Usar la prueba para la parada temprana.** Si la parada temprana mira el conjunto de prueba, la prueba ya
  participó en el ajuste del número de épocas.
- **Volver a ajustar después de ver la prueba.** "No me gustó el resultado en la prueba, voy a probar otra rejilla":
  en ese momento la prueba pasó a ser validación.

Por último, hay una cuestión de justicia en las comparaciones. Si comparamos un *gradient boosting* ajustado con 200
configuraciones contra una regresión logística con los valores por defecto, no estamos viendo qué modelo es mejor,
sino a cuál le dedicamos más esfuerzo. **Los modelos que se comparan tienen que recibir un presupuesto de ajuste
parecido, y ese presupuesto se reporta.**

> **Para ampliar.** C7, sección 4 (validación cruzada anidada). C5, el factor $M$ y el sobreajuste al conjunto de
> validación. Abu-Mostafa et al., *Learning from Data*, secciones 4.3 (*Validation*) y 5.3 (*Data snooping*),
> pp. 173–178.

---

## 4. El modelo en el tiempo

### Cuando cae el supuesto

Hasta aquí, todo lo que hicimos supone que los datos son **independientes e idénticamente distribuidos** (i.i.d.), es
decir, que los ejemplos con los que entrenamos y evaluamos vienen de la misma distribución que los que el modelo va a
ver cuando lo usemos. El supuesto es razonable: si el futuro no se pareciera en nada al pasado, no habría nada que
aprender. Pero para un modelo que va a estar funcionando meses o años, es pedir demasiado.

Abu-Mostafa y sus coautores lo ilustran con un ejemplo de **sesgo de muestreo**. Una firma entrena un sistema para
comprar y vender acciones, pero solo con datos de períodos en que el mercado "se portaba bien". El resultado es un
sistema en el que solo se puede confiar mientras el mercado se siga portando bien. Con la degradación en el tiempo
pasa lo mismo: el modelo aprendió de una muestra del pasado, y el presente ya no se parece a esa muestra.

> **Para ampliar.** Russell y Norvig, sección 19.8.6 (introducción, sobre el supuesto i.i.d.) y sección 19.9.5
> (*nonstationarity*, con el ejemplo del spam). Abu-Mostafa et al., *Learning from Data*, sección 5.2 (*Sampling
> bias*), p. 171.

### Tipos de deriva

A ese cambio de la distribución en el tiempo se le llama **deriva** (*drift*). Para distinguir los tipos de deriva
ayuda escribir la distribución conjunta como

$$P(X, Y) = P(X)\, P(Y \mid X).$$

Puede cambiar cualquiera de los dos factores, y no da lo mismo cuál:

| Tipo | Qué cambia | En el detector de fraude | ¿Cambia la frontera de decisión? |
|---|---|---|---|
| Deriva de datos o de covariables | $P(X)$ | El banco lanza el pago con código QR y aparecen transacciones con montos y horarios que casi no había antes | No necesariamente |
| Deriva de etiquetas | $P(Y)$ | En diciembre sube la proporción de fraudes | No, pero cambia el umbral adecuado |
| Deriva de concepto | $P(Y \mid X)$ | Los estafadores aprenden que los montos pequeños no se bloquean y fraccionan sus cargos: transacciones que antes eran legítimas casi siempre, ahora no | Sí |

La más grave es la **deriva de concepto**, porque la relación que aprendió el modelo ya no es verdad. Recalibrarlo
no alcanza; hay que volver a aprender. La deriva de covariables puede no hacer daño si el modelo generaliza bien a la
región nueva del espacio, o puede ser peligrosa si esa región casi no aparecía en el entrenamiento, porque entonces el
modelo extrapola sin que nadie se entere. A veces se le dice **virtual** a la deriva que cambia los datos pero no la
frontera, y **real** a la que sí la cambia.

También importa **cómo** ocurre en el tiempo. Puede ser **abrupta** (una campaña de fraude nueva que empieza un
lunes), **gradual** o **incremental** (los hábitos de pago que van cambiando poco a poco), o **recurrente** (los
patrones de diciembre, que vuelven cada año). Y ojo, no hay que confundirla con el **ruido**: unos cuantos días malos
no son una deriva. Separar una cosa de la otra es justamente lo difícil para los detectores que vamos a ver más
adelante.

Russell y Norvig mencionan un caso extremo: que cambie el **esquema** de los datos. Por ejemplo, un filtro de spam de
correo que de pronto tiene que clasificar también mensajes de texto, de voz o videos.

> **Para ampliar.** Murphy, sección 19.2.5 (*domain adaptation*), p. 637, para el cambio de distribución entre el
> entrenamiento y el uso. Gama et al. (2014), *(externa)*: la revisión de referencia sobre la deriva de concepto, con
> esta taxonomía y los métodos de detección y adaptación. La bibliografía del curso no trae una taxonomía completa.

### Por qué la degradación pasa inadvertida

Un modelo no avisa cuando empieza a fallar. Sigue dando predicciones con la misma seguridad de siempre. Y en
problemas como el nuestro hay dos cosas que lo hacen todavía más difícil de notar:

- **Las etiquetas llegan tarde.** Sabemos que una transacción era fraude cuando el cliente reclama, y eso puede ser
  semanas después. Mientras tanto, no podemos medir la sensibilidad.
- **El modelo influye en sus propias etiquetas.** Una transacción que el detector bloquea no llega a completarse, así
  que nunca vamos a saber si era fraude. Los datos con los que reentrenaríamos ya vienen filtrados por el propio
  modelo. Es un **lazo de retroalimentación**: el mismo sesgo de muestreo de antes, solo que esta vez lo provocamos
  nosotros.

### Monitorear

Como el modelo no avisa, hay que vigilarlo. Monitorear es medir algunas cantidades todo el tiempo y compararlas con
una referencia. Qué medimos depende de lo que tengamos a mano:

- **El rendimiento**, si llegan etiquetas: sensibilidad, precisión, costo esperado. Es lo más directo, pero llega con
  retraso.
- **Las entradas**, o sea, la distribución de cada atributo. Así se detecta la deriva de covariables antes de que se
  note en el rendimiento.
- **Las salidas**: la distribución de las probabilidades que da el modelo, o la proporción de transacciones que
  bloquea. Esto no necesita etiquetas, y un cambio brusco ya es una señal de alarma.
- **Los datos en sí**: valores faltantes, categorías nuevas, cambios de formato. Muchas veces, cuando un modelo "se
  cae", lo que hay en realidad es un error en los datos de entrada (C6).

La forma más básica de comparar es con **dos ventanas**: una de referencia (por ejemplo, el mes con que se validó el
modelo) y otra actual (la última semana). Si las distribuciones son distintas, algo cambió. Para decidir si lo son se
usan **pruebas sobre distribuciones**, como la de Kolmogorov-Smirnov para variables continuas o la $\chi^2$ para
categóricas. Aquí hay que recordar dos cosas de la C7. Con decenas de atributos y una prueba diaria, las
**comparaciones múltiples** nos van a dar falsas alarmas seguro. Y con muchos datos, una diferencia **significativa**
puede no tener ninguna importancia práctica. El tamaño de la ventana también es un compromiso: una ventana corta
detecta antes, pero confunde el ruido con la deriva; una larga es más estable, pero tarda en reaccionar.

Cuando sí hay etiquetas, se puede vigilar el error directamente con **detectores de deriva**. Veamos dos ideas:

- **DDM** (*drift detection method*) sigue la tasa de error del modelo sobre el flujo y su desviación. Da una
  **advertencia** cuando el error sube unas dos desviaciones por encima del mínimo que ha visto, y declara **deriva**
  cuando sube unas tres.
- **ADWIN** (*adaptive windowing*) trabaja con una ventana de tamaño variable. Cada vez que llega un dato, revisa si
  hay algún punto que divida la ventana en dos partes con medias de error significativamente distintas. Si lo hay,
  descarta la parte vieja. De esa forma la ventana crece mientras todo está estable y se achica cuando hay un cambio.

> **Para ampliar.** Russell y Norvig, sección 19.9.5 (*Operation, monitoring, and maintenance*), con la figura 19.28,
> una lista de comprobación de pruebas y monitoreo para modelos en producción. Gama et al. (2014), *(externa)*, para
> DDM, ADWIN y otros.

### Políticas de reentrenamiento

Detectar el problema no es suficiente; después hay que decidir qué hacer. Las opciones, de menos a más reactivas,
son:

1. **Reentrenar periódicamente**, por calendario: cada mes, cada semana. Es simple y predecible, pero a veces
   reentrena sin necesidad y otras reacciona tarde a un cambio abrupto.
2. **Reentrenar cuando salta un detector.** Reacciona cuando hace falta, pero depende de que el detector funcione
   bien.
3. **Aprender de forma continua**, actualizando el modelo con cada dato nuevo. Eso es el aprendizaje online, que
   vemos en la sección siguiente.

También hay que decidir **con qué datos** reentrenar: todo el histórico (es estable, pero arrastra patrones que
quizás ya no sirven), una **ventana deslizante** con lo más reciente (se adapta, pero olvida), o todo el histórico
con **pesos que bajan con la antigüedad**.

Russell y Norvig plantean la pregunta de fondo: ¿qué es mejor, un modelo bien probado pero hecho con datos viejos, o
uno hecho con los datos más recientes pero que todavía no se ha probado en uso real? No hay una respuesta general.
Hay problemas que necesitan un modelo nuevo cada hora y otros que aguantan el mismo durante meses. Lo que sí vale
siempre es que **la versión nueva se valida antes de reemplazar a la vieja**. Lo habitual es el esquema de
**campeón y retador**: el modelo nuevo funciona en paralelo, en sombra o con una fracción pequeña del tráfico, y solo
reemplaza al actual si lo supera. Esa validación tiene que ser **temporal**: se entrena con el pasado y se evalúa con
lo que vino después, nunca con una validación cruzada que mezcle fechas. Es lo mismo que decíamos en la C7: la
partición tiene que imitar el uso.

Todo esto se puede resumir en un **plan de monitoreo**. Para el detector de fraude podría quedar así:

| Qué se mide | Referencia | Umbral de alarma | Frecuencia | Acción |
|---|---|---|---|---|
| Proporción de transacciones bloqueadas | Mes de validación | Cambio de más del 30 % | Diaria | Revisar los datos de entrada |
| Distribución del monto y del canal | Mes de validación | Kolmogorov-Smirnov con corrección por comparaciones múltiples | Semanal | Analizar la región nueva; valorar reentrenar |
| Sensibilidad sobre fraudes confirmados | Estimación de la validación | Por debajo del límite inferior de su intervalo | Mensual (por el retraso de las etiquetas) | Reentrenar y validar como retador |

> **Para ampliar.** Russell y Norvig, sección 19.9.5 (la frescura del modelo y el compromiso entre un modelo online y
> uno reconstruido desde cero).

---

## 5. Aprendizaje online

### Del lote al flujo

Hasta ahora hemos aprendido **por lotes** (*batch*): juntamos los datos, entrenamos una vez y el modelo queda fijo
hasta el próximo entrenamiento. En el **aprendizaje online** (*online learning*) los datos llegan como un **flujo**,
de uno en uno o en grupos pequeños, y el modelo se actualiza con cada uno sin entrenar de nuevo desde cero. El
esquema siempre es el mismo:

```text
APRENDIZAJE-ONLINE(flujo de ejemplos)
    inicializar el modelo h
    para cada ejemplo x_t que llega:
        ŷ_t ← h(x_t)                       # 1. predecir con el modelo actual
        recibir la respuesta correcta y_t
        registrar la pérdida ℓ(ŷ_t, y_t)   # 2. evaluar antes de aprender
        h ← ACTUALIZAR(h, x_t, y_t)        # 3. aprender del ejemplo
```

Fíjense en el paso 2: cada ejemplo se usa **primero para probar y después para entrenar**, así que el modelo siempre
se evalúa con datos que todavía no ha visto. A esta forma de evaluar se le llama ***prequential*** (de *predictive
sequential*). En nuestro detector hay un detalle: la respuesta correcta $y_t$ no llega enseguida, sino cuando se
confirma o se descarta el fraude, así que en la práctica la actualización va con retraso.

> **Para ampliar.** Russell y Norvig, sección 19.8.6 (*Online learning*). Duda et al., sección 6.8.13 (entrenamiento
> on-line, estocástico o por lotes).

### La actualización incremental

En muchos modelos, `ACTUALIZAR` es un paso de **descenso por gradiente estocástico** (SGD): movemos los parámetros
un poco en la dirección que reduce la pérdida **en ese ejemplo**,

$$w \leftarrow w - \eta\, \nabla_w\, \ell(w;\, x_t, y_t),$$

donde $\eta$ es la tasa de aprendizaje. No hace falta guardar el histórico, porque todo lo aprendido queda en los
parámetros, así que la **memoria que se usa es acotada**. Por eso el aprendizaje online también sirve cuando hay
demasiados datos para que quepan en memoria, aunque no cambien con el tiempo.

> **Para ampliar.** Murphy, sección 8.4 (*Stochastic gradient descent*), pp. 292–301.

### Una garantía: el arrepentimiento

¿Se puede garantizar algo si los datos cambian sin avisar, o incluso si alguien los escoge a propósito para que
fallemos, como hacen nuestros estafadores? Se puede, siempre que la garantía sea relativa.

Russell y Norvig lo muestran con un ejemplo. Tenemos $K$ "expertos" (pueden ser $K$ modelos distintos) que todos los
días predicen algo, y queremos combinar lo que dicen. El algoritmo de **mayoría ponderada aleatorizada** le tiene a
cada uno más o menos confianza según cómo le haya ido:

```text
MAYORÍA-PONDERADA-ALEATORIZADA(K expertos, β con 0 < β < 1)
    w_1, …, w_K ← 1
    para cada problema:
        recibir las predicciones ŷ_1, …, ŷ_K de los expertos
        elegir un experto k* al azar con probabilidad proporcional a w_k*
        responder ŷ_k*
        recibir la respuesta correcta y
        para cada experto k que se equivocó (ŷ_k ≠ y):
            w_k ← β · w_k                  # se le quita confianza
        normalizar los pesos para que sumen 1
```

Para medir qué tan bueno es se usa el **arrepentimiento** (*regret*): cuántos errores más comete que el mejor
experto, mirando hacia atrás. Si el mejor experto se equivocó $M^*$ veces, el algoritmo se equivoca $M$ veces, con

$$M < \frac{M^* \ln(1/\beta) + \ln K}{1 - \beta}.$$

Con $K = 10$ expertos y $\beta = 1/2$ queda $M < 1{,}39\,M^* + 4{,}6$. Y esta cota vale para **cualquier** secuencia
de datos, incluso una elegida por un adversario.

El parámetro $\beta$ refleja el compromiso de fondo del aprendizaje online. Con $\beta$ cerca de 1, cada error se
castiga poco: el algoritmo es estable y a la larga se adapta si cambia el mejor experto, pero al principio tarda en
dejar de hacerles caso a los malos. Con $\beta$ cerca de 0 reacciona enseguida, pero basta una racha de mala suerte
de un buen experto para que lo descarte. Si queremos que reaccione rápido, perdemos estabilidad, y al revés.

> **Para ampliar.** Russell y Norvig, sección 19.8.6: el algoritmo, la cota y el aprendizaje sin arrepentimiento
> (*no-regret learning*).

### Ventajas y retos

El aprendizaje online tiene tres ventajas:

- **Latencia baja**: lo que se aprende entra en el modelo casi enseguida, sin esperar al próximo reentrenamiento.
- **Adaptación continua**: si los patrones cambian, el modelo los va siguiendo sin que nadie intervenga.
- **Menor costo**: actualizar con un ejemplo es mucho más barato que reentrenar con todo el histórico.

Pero también trae problemas. Estos son los cuatro principales, con lo que se suele hacer para mitigarlos:

| Reto | Qué pasa | Mitigaciones |
|---|---|---|
| Deriva de concepto | Lo aprendido deja de valer | Ventanas o decaimiento exponencial que den más peso a lo reciente; detectores (sección 4) |
| Olvido catastrófico | Al adaptarse a lo reciente, el modelo olvida patrones viejos que todavía valen | Mezclar lo nuevo con una muestra guardada del pasado (*replay*); limitar cuánto pueden cambiar los parámetros; vigilar el rendimiento en un conjunto estable de control |
| La tasa de aprendizaje | Si es muy alta, el modelo oscila y persigue el ruido; si es muy baja, no se adapta | Programaciones de la tasa y métodos adaptativos como Adam; volver a una versión anterior si la métrica reciente empeora |
| El orden de los datos | Si durante un rato llegan solo ejemplos de una clase, el modelo se sesga hacia ella | Acumular pequeños lotes y barajarlos antes de actualizar; muestrear por clase |

La tercera fila nos devuelve a la sección 1: ajustar la tasa de aprendizaje mientras se aprende es **control on-line
de un hiperparámetro**. En el aprendizaje online hay que estar ajustando hiperparámetros todo el tiempo, y encima con
datos que cambian.

> **Para ampliar.** Murphy, secciones 8.4.3 (cómo elegir la tasa de aprendizaje) y 8.4.6 (AdaGrad, RMSProp y Adam).

### ¿Reentrenar periódicamente o aprender en línea?

Aquí tampoco hay una respuesta que sirva para todo (otra vez la C5), pero sí hay criterios:

| A favor del reentrenamiento periódico | A favor del aprendizaje online |
|---|---|
| Los cambios son lentos | Los cambios son rápidos o los provoca un adversario |
| Cada versión tiene que validarse y auditarse antes de usarse | Equivocarse por un rato es barato y reversible |
| Las etiquetas llegan con mucho retraso | Las etiquetas llegan enseguida |
| El modelo no admite actualización incremental | El volumen de datos hace caro reentrenar |

En el detector de fraude pesan los dos lados. Los estafadores cambian rápido y juegan en contra nuestra, y eso
favorece el aprendizaje online. Pero las etiquetas tardan semanas y cada error del modelo cuesta dinero y clientes, y
eso favorece tener versiones validadas. Una solución bastante común es combinar las dos cosas: un modelo base que se
reentrena y se valida cada cierto tiempo, y un componente online pequeño, vigilado, que reacciona a los patrones
nuevos entre un reentrenamiento y el siguiente.

---

## 6. Comunicar los límites

### Qué es un límite

Ningún modelo funciona en todas partes y para siempre, así que en un informe hay que decir también **dónde** deja de
funcionar. Un límite bien escrito es **concreto** y **verificable**, y casi siempre responde a alguna de estas
preguntas:

- **Dominio de validez.** ¿Con qué población y en qué período se entrenó y se evaluó? ¿Con quién no se probó?
- **Incertidumbre.** ¿Cuánto puede variar la estimación? Un número sin su intervalo dice muy poco (C7).
- **Supuestos.** ¿Qué supusimos que podría no cumplirse? ¿Que las etiquetas son correctas? ¿Que la distribución no
  cambia?
- **Fallos conocidos.** ¿En qué casos se equivoca el modelo, y qué consecuencias tiene?
- **Lo que no se probó.** Lo que no se evaluó, no se sabe. Decirlo no le quita valor al trabajo, y evita que otra
  persona use el modelo donde no debe.

Para organizar todo esto sirven las ***model cards***: una ficha corta que acompaña al modelo y recoge para qué está
pensado, con qué datos se evaluó, sus métricas separadas por grupos y sus limitaciones.

### Cuando no hay solución

A veces lo honesto es reportar que **no se encontró nada**: que el modelo no le gana al baseline, o que la prueba de
permutación de la C7 no permite descartar que acierte por azar. Eso también es un resultado, y se reporta igual que
uno positivo. Un informe que esconde un resultado negativo detrás de una métrica bien escogida hace más daño que no
tener informe, porque alguien va a tomar decisiones basándose en él.

### El límite en una frase

Comparen estas dos frases sobre nuestro detector:

> ✗ "El modelo detecta el fraude con una exactitud del 99 %."

Con un 1 % de fraudes, un modelo que nunca marca nada también tiene un 99 % de exactitud. Además, la frase no dice
cómo se midió, con qué datos, ni hasta cuándo vale.

> ✓ "Con transacciones de tarjetas nacionales de enero a junio de 2026, el detector identifica el 82 % de los fraudes
> confirmados (intervalo del 95 %: 78–86 %). No se evaluó con pagos por código QR, que empezaron en septiembre, y la
> estimación supone que los fraudes confirmados son representativos de todos, lo que no se puede comprobar porque las
> transacciones bloqueadas no se etiquetan."

La segunda frase luce menos, pero dice exactamente cuánto vale el trabajo y dónde deja de valer.

> **Para ampliar.** Mitchell et al. (2019), *Model cards for model reporting*, *(externa)*. El artículo figura en la
> lista de referencias de Russell y Norvig.

---

## 7. Qué llevarse de esta nota

1. **Ajustar hiperparámetros es buscar.** La función objetivo es cara, ruidosa y sin gradiente, y el espacio mezcla
   variables continuas, enteras, categóricas y condicionales.
2. **La búsqueda aleatoria es el baseline del ajuste.** Le gana a la rejilla porque son pocos los hiperparámetros que
   importan, y cualquier método más sofisticado tiene que superarla para justificarse.
3. **Las estrategias más elaboradas ahorran evaluaciones** de dos formas: aprendiendo de las anteriores
   (optimización bayesiana) o descartando pronto las malas (*racing*, *successive halving*).
4. **Mientras más se busca, más optimista sale el mejor puntaje.** El ajuste va dentro de la validación cruzada
   anidada, y el presupuesto de ajuste se reporta y se iguala al comparar.
5. **Un modelo desplegado se degrada** porque el mundo cambia: deriva de datos, de etiquetas o de concepto. Como no
   avisa, hay que monitorear entradas, salidas y rendimiento, y tener una política de reentrenamiento con validación
   temporal.
6. **El aprendizaje online se adapta continuamente**, pero tiene riesgos: el olvido, la sensibilidad a la tasa de
   aprendizaje y al orden de los datos. Mientras más rápido se adapta, menos estable es.
7. **Los límites de una solución se escriben** de forma concreta y verificable, incluido el caso en que no hay
   solución.

---

## 8. Ejercicios

**1.** Un compañero quiere ajustar un bosque aleatorio con 5 hiperparámetros y 6 niveles por hiperparámetro, usando
validación cruzada de 10 folds. Cada entrenamiento tarda 30 segundos. *(a)* ¿Cuánto tardaría la búsqueda en
rejilla completa? *(b)* Si tiene 8 horas de cómputo, ¿cuántas configuraciones podría evaluar? *(c)* Propón una
estrategia para ese presupuesto y justifícala.

**2.** Completa la tabla de correspondencias de la sección 1 con dos filas más, pensando en algún aspecto del ajuste
de metaheurísticas de la C3 que tenga su equivalente al ajustar un modelo.

**3.** ¿Cuántas configuraciones al azar hacen falta para tener al menos un 99 % de probabilidad de encontrar una en el
mejor 1 % del espacio? ¿Y en el mejor 10 %? ¿Por qué el resultado no depende del número de hiperparámetros?

**4.** Ejecuta a mano *successive halving* con $\eta = 2$ sobre ocho configuraciones A–H. La tabla da el error de
validación de cada una con cada presupuesto (número de árboles). *(a)* ¿Cuál gana? *(b)* ¿Cuál habría ganado si se
hubieran entrenado todas con 400 árboles? *(c)* ¿Qué propiedad de esa configuración explica la diferencia?

| Árboles | A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|---|
| 50 | 0,21 | 0,18 | 0,30 | 0,19 | 0,25 | 0,17 | 0,28 | 0,20 |
| 100 | 0,19 | 0,16 | 0,22 | 0,17 | 0,20 | 0,16 | 0,24 | 0,18 |
| 200 | 0,18 | 0,15 | 0,14 | 0,16 | 0,17 | 0,15 | 0,20 | 0,17 |
| 400 | 0,18 | 0,15 | 0,11 | 0,16 | 0,16 | 0,15 | 0,19 | 0,17 |

**5.** Un equipo reporta: "Tras probar 2 000 configuraciones con optimización bayesiana, nuestra red alcanza un F1 de
0,91 en validación, frente a 0,84 de la regresión logística con sus valores por defecto. La red es claramente
superior." Señala todos los problemas que tiene esta afirmación y di qué habría que hacer para sostener la
comparación.

**6.** Para cada situación, di qué tipo de deriva es (de covariables, de etiquetas o de concepto) y si crees que el
modelo necesita reentrenarse:
*(a)* Un modelo de demanda eléctrica de La Habana entrenado antes de que se generalizaran los paneles solares en las
viviendas.
*(b)* Un clasificador de spam entrenado cuando los mensajes eran en su mayoría correos, que ahora recibe sobre todo
mensajes de WhatsApp con el mismo tipo de contenido.
*(c)* Un modelo de diagnóstico de una enfermedad respiratoria entrenado fuera de temporada, usado durante una
epidemia.
*(d)* Un modelo que predice el abandono de los clientes de una empresa de telefonía, después de que la competencia
lanzó una oferta muy agresiva.

**7.** Diseña un plan de monitoreo, con la estructura de la tabla de la sección 4, para un modelo que predice qué
estudiantes de la facultad están en riesgo de abandonar la carrera. Ten en cuenta cuándo llegan las etiquetas.

**8.** Una empresa de comercio electrónico quiere un sistema de recomendación de productos y no sabe si reentrenarlo
cada semana o usar aprendizaje online. ¿Qué le recomendarías, según los criterios de la sección 5? ¿Qué riesgo
vigilarías especialmente en cada opción?

**9.** En el algoritmo de mayoría ponderada aleatorizada con $K = 10$, calcula la cota para $\beta = 3/4$ y compárala
con la de $\beta = 1/2$. ¿Cuál preferirías si el mejor experto cambia con frecuencia? ¿Y si es siempre el mismo?

**10.** Escribe en una frase el límite principal del modelo de riesgo de abandono del ejercicio 7, con las
características de la sección 6: concreta, verificable y con su dominio de validez.

<!--
## 9. Soluciones

**1.** (a) 6^5 = 7 776 configuraciones × 10 folds = 77 760 entrenamientos × 30 s = 2 332 800 s, unos 27 días.
(b) 8 h = 28 800 s; cada configuración cuesta 10 × 30 = 300 s, así que caben 96 configuraciones. (c) Por ejemplo,
búsqueda aleatoria con unas 90 configuraciones: con 60 ya hay un 95 % de probabilidad de caer en el mejor 5 %
(sección 2). Si el número de árboles se puede usar como recurso, successive halving permite empezar con muchas más
configuraciones baratas. Una buena respuesta menciona que el presupuesto se reporta y que la evaluación final va con
validación anidada o con una prueba reservada.

**2.** Respuestas posibles: "el tiempo de cómputo por corrida de la metaheurística" corresponde a "el costo de
entrenar"; "la selección de instancias representativas" corresponde a "una partición que imite el uso"; "el número de
evaluaciones de la función objetivo como presupuesto" corresponde a "el número de configuraciones × folds"; "el
ajuste on-line del enfriamiento del recocido" corresponde a "la programación de la tasa de aprendizaje".

**3.** Se busca el menor n con 1 − (1 − p)^n ≥ 0,99, o sea n ≥ ln(0,01) / ln(1 − p). Para p = 0,01: n ≥ 4,605 /
0,01005 ≈ 458,2, es decir, 459. Para p = 0,10: n ≥ 4,605 / 0,1054 ≈ 43,7, es decir, 44. No depende del número de
hiperparámetros porque el argumento solo usa la probabilidad de caer en una región que ocupa una fracción p del
espacio, sin importar cuántas dimensiones tenga. Lo que sí cambia con la dimensión es qué tan buena es esa región: el
mejor 1 % de un espacio grande puede estar lejos del óptimo.

**4.** Ronda 1 (50 árboles): se quedan las 4 mejores, F (0,17), B (0,18), D (0,19) y H (0,20). Ronda 2 (100 árboles):
F 0,16, B 0,16, D 0,17, H 0,18; pasan F y B (empatadas, cualquiera de los dos criterios de desempate da el mismo
final). Ronda 3 (200 árboles): B 0,15, F 0,15; empate, se decide por ejemplo a favor de B. (a) Gana B (o F, con
error 0,15). (b) Con 400 árboles habría ganado C, con 0,11. (c) C arranca lento: con 50 árboles es la peor (0,30),
pero es la que más mejora con más presupuesto, por ejemplo porque tiene una tasa de aprendizaje pequeña. Es el riesgo
de successive halving que menciona la sección 2 y que Hyperband intenta atenuar.

**5.** (a) El 0,91 es el mejor de 2 000 estimaciones de validación: es optimista (factor M de la C5); hace falta
validación anidada o una prueba reservada. (b) La comparación es injusta: 2 000 configuraciones frente a cero
ajustes; hay que dar un presupuesto comparable a los dos modelos. (c) No hay medida de variabilidad ni prueba
pareada (C7). (d) "Claramente superior" excede lo que un experimento sobre un conjunto de datos permite afirmar. (e)
No se dice si el F1 es la métrica adecuada para el costo de los errores. Para sostener una comparación: validación
anidada con los mismos folds para los dos, presupuesto de ajuste comparable y reportado, y prueba pareada con
corrección de Nadeau y Bengio.

**6.** (a) Cambia la relación entre las variables de entrada (hora, temperatura) y la demanda de la red: deriva de
concepto; hay que reentrenar. (b) Cambia P(X) (otro tipo de mensaje) pero no necesariamente la relación entre el
contenido y la etiqueta: deriva de covariables; puede funcionar si los atributos generalizan, pero hay que
verificarlo con datos del nuevo canal. (c) Cambia sobre todo P(Y), la prevalencia: deriva de etiquetas; puede bastar
con ajustar el umbral, aunque si cambian también los síntomas típicos habría deriva de concepto. (d) Cambia
P(Y | X): clientes con el mismo perfil ahora abandonan más; deriva de concepto, abrupta; hay que reentrenar.

**7.** Debe notar que la etiqueta (abandonó o no) llega al final del curso o más tarde, así que el rendimiento solo se
puede medir una o dos veces al año. Por eso el plan tiene que apoyarse en las entradas (notas parciales, asistencia,
cambios en el ingreso, nuevas carreras o modalidades) y en las salidas (proporción de estudiantes marcados en riesgo,
por facultad o por año). Buenas respuestas mencionan el lazo de retroalimentación: si el modelo dispara una tutoría y
el estudiante no abandona, no se sabe si el modelo se equivocó o la tutoría funcionó.

**8.** Argumentos para online: los gustos y el catálogo cambian rápido, las etiquetas (clics y compras) llegan
enseguida y equivocarse por un rato es barato. Para periódico: más fácil de validar y auditar, menos riesgo de que
una campaña o un error en los datos arrastre al modelo. Riesgo a vigilar en el periódico: que reaccione tarde a una
temporada o a una moda. En el online: el olvido catastrófico (olvidar los gustos estables por perseguir la moda de la
semana) y el lazo de retroalimentación (solo se observan clics en lo que el propio sistema recomienda).

**9.** Con β = 3/4: ln(4/3) ≈ 0,288 y 1 − β = 0,25, así que M < 1,15 M* + ln(10)/0,25 ≈ 1,15 M* + 9,2. Con β = 1/2:
M < 1,39 M* + 4,6. Si el mejor experto cambia con frecuencia, conviene β más pequeño (1/2), que deja de confiar
antes en un experto que empieza a fallar, aunque pague más por cada error del mejor. Si el mejor es siempre el mismo,
conviene β más cercano a 1: a la larga se pierde menos por cada error del mejor (factor 1,15 frente a 1,39), y el
término fijo, más grande, pesa poco cuando hay muchos problemas.

**10.** Respuesta abierta. Se valora que diga con qué datos o escenarios se probó, qué incertidumbre tiene el
resultado, y qué supuesto o escenario no cubierto podría invalidarlo. Una frase del tipo "el modelo funciona bien" no
cumple ninguna de las tres condiciones.
-->

---

## Referencias

**Libros de la bibliografía del curso**

Russell, S. y Norvig, P. *Artificial Intelligence: A Modern Approach*, 4.ª edición, Pearson, 2020. Secciones 19.4.4
(ajuste de hiperparámetros), 19.8.6 (aprendizaje online y arrepentimiento) y 19.9.5 (operación, monitoreo y
mantenimiento).

Talbi, E.-G. *Metaheuristics: From Design to Implementation*, Wiley, 2009. Sección 1.6 (ajuste de parámetros
off-line y on-line, diseño de experimentos y meta-optimización).

Gendreau, M. y Potvin, J.-Y. (eds.). *Handbook of Metaheuristics*, 3.ª edición, Springer, 2019. Capítulo 17: Stützle,
T. y López-Ibáñez, M., "Automated design of metaheuristic algorithms" (configuración automática, ParamILS, SMAC,
irace y selección de algoritmos).

Abu-Mostafa, Y., Magdon-Ismail, M. y Lin, H. *Learning from Data*, AMLBook, 2012. Secciones 4.3 (validación), 5.2
(sesgo de muestreo) y 5.3 (espionaje de datos).

Murphy, K. *Probabilistic Machine Learning: An Introduction*, MIT Press, 2022. Secciones 8.4 (descenso por gradiente
estocástico y tasas de aprendizaje), 14.3.6 (búsqueda de arquitecturas), 17.2 (procesos gaussianos) y 19.2.5
(adaptación de dominio).

Duda, R., Hart, P. y Stork, D. *Pattern Classification*, 2.ª edición, Wiley, 2001. Sección 6.8.13 (entrenamiento
on-line, estocástico o por lotes).

**Fuentes externas**

Bergstra, J. y Bengio, Y. "Random search for hyper-parameter optimization", *Journal of Machine Learning Research*,
13, 281–305, 2012.

Li, L., Jamieson, K., DeSalvo, G., Rostamizadeh, A. y Talwalkar, A. "Hyperband: A novel bandit-based approach to
hyperparameter optimization", *Journal of Machine Learning Research*, 18(185), 1–52, 2018.

Hutter, F., Kotthoff, L. y Vanschoren, J. (eds.). *Automated Machine Learning: Methods, Systems, Challenges*,
Springer, 2019. Capítulo 1: Feurer, M. y Hutter, F., "Hyperparameter optimization". De acceso abierto.

Gama, J., Žliobaitė, I., Bifet, A., Pechenizkiy, M. y Bouchachia, A. "A survey on concept drift adaptation", *ACM
Computing Surveys*, 46(4), artículo 44, 2014.

Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D. y Gebru, T.
"Model cards for model reporting", *Proceedings of the Conference on Fairness, Accountability, and Transparency*, 2019.

<div class="nota-ia">
Nota sobre la elaboración de este texto: redactado con asistencia de inteligencia artificial, con el modelo Claude
Opus 5.5 de Anthropic (identificador <code>claude-opus-5-5</code>), en noviembre de 2026, a partir del esquema, las
fuentes y las indicaciones de la profesora de la asignatura. La figura 1 se generó con un script elaborado con el mismo
modelo.
</div>
