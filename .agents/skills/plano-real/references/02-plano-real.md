# Fase 2, el plano real
El entregable central del sistema: por dónde camina el trabajo de verdad, cuántas veces cambia de manos, dónde se atora y dónde alguien tiene que decidir. Casi siempre contradice lo que el dueño creía de su propia operación, y esa contradicción es el producto.
## Cómo se camina un caso
El plano no se dibuja en una junta ni se reconstruye de memoria. Se camina:
1. Elegir el caso: el más reciente, completo y representativo. Fecha exacta.
2. Sentarse con quien lo ejecuta, con el caso o su registro delante.
3. Recorrerlo en orden, paso por paso, preguntando qué se hizo, dónde se anotó y quién lo tocó después.
4. En cada paso, marcar: quién, en qué sistema, qué entró, qué salió, cuánto trabajó y cuánto esperó.
5. Marcar cada cambio de manos y cada punto donde alguien decidió algo.
6. Al terminar, contar los tres números del plano con la persona delante.
7. Caminar un segundo caso de una variante distinta, aunque sea corto, para ver qué cambia.
Casos mínimos antes de cerrar el plano: uno del caso frecuente, uno de un cliente o variante distinta, uno con excepción, y uno que haya sido urgente. Si alguno no existe en la ventana, se anota y se dice, no se rellena con lo que se supone.
## El modelo de datos del plano
El flujo son **dos tablas**, no una lista. Una lista no puede representar un grafo: siempre sale un dibujo lineal aunque el proceso no lo sea.

**Tabla de nodos**, una fila por paso del proceso:
| id | texto | forma | quien | sistema | trabajo | espera | evidencia |
|---|---|---|---|---|---|---|---|
**Tabla de rutas**, una fila por cada camino entre dos nodos:
| desde | hacia | etiqueta | tipo |
|---|---|---|---|
Valores fijos que no se improvisan:
- **forma**: `inicio`, `fin`, `actividad`, `documento`, `datos`, `decision`, `demora`, `base-de-datos`, `almacenamiento`, `preparacion`, `subproceso`, `conector`, `entrada-manual`. De ahí sale el símbolo.
- **tipo** de ruta: `normal`, `excepcion`, `retrabajo`, `rechazo`. Un `retrabajo` es un camino que vuelve a un paso anterior. Un `rechazo` cierra el caso sin reincorporarse.
- **etiqueta**: la condición escrita con palabras del cliente, no un sí o un no genérico. En un rombo, la etiqueta es la respuesta que abre ese camino.
- **trabajo** y **espera**: en minutos, horas o días, y la espera es el tiempo en que el caso no avanza porque alguien no lo empujó. Confundirlas destruye el diagnóstico: casi siempre el problema no es que trabajen lento, es que el caso espera.
- **evidencia**: la clase y su recibo, en el formato de las convenciones. Un paso `dicho` se marca y no se toca.
Si el expediente ya traía la tabla vieja de pasos, el generador la convierte a nodos y rutas: la arista principal es la cadena, y cada excepción se vuelve un nodo con su camino de ida y su regreso.
## Los tres contadores del plano
1. **Manos**: cuántas veces cambia de dueño el caso. Cada cambio de manos es un lugar donde se puede caer.
2. **Esperas**: cuántos tiempos muertos acumula. Se suman y se expresan también en días de calendario, no solo en horas.
3. **Puntos de decisión**: dónde alguien tiene que juzgar algo. Cada uno es un lugar donde el proceso depende de que esa persona esté.
Estos tres números son los que el cliente entiende de inmediato, más que cualquier diagrama.
## El diagrama
Lo genera `scripts/generar-diagrama.py` desde las dos tablas: un SVG profesional en el entregable, y un bloque Mermaid dentro de la nota como vista editable. El dibujo no se edita a mano; si las tablas cambian y el diagrama no, la auditoría lo marca vencido.
- **Un rombo declara sus salidas.** Un rombo con una sola salida no es una decisión, es un adorno: o tiene dos o más rutas con su etiqueta, o la forma está mal elegida.
- **Los caminos se ven separarse y volver a juntarse.** Si todas las rutas terminan en el mismo nodo siguiente, en fila, el proceso no está mapeado: está resumido.
- **El retrabajo regresa por el carril exterior**, con línea punteada azul, y su etiqueta dice a dónde vuelve.
- **Una excepción que no se reincorpora es un cierre terminal**, y se dibuja como tal, no como una nota al lado.
- Cuando el flujo no cabe con aire en una hoja, se corta y se une con el símbolo de conector (A, B, C). El generador lo hace solo.
Regla: si el diagrama no se puede leer en un teléfono, se parte en dos hojas.
## Cómo se mapea una excepción
Una excepción no se documenta como ruido ni como anécdota: se documenta como una ruta, con cinco cosas:
1. **El disparador**: qué la provoca, en una frase.
2. **Quién la atiende** y con qué permiso.
3. **A dónde desvía** y en qué paso se reincorpora.
4. **Cuántas veces pasa**, contadas en la ventana declarada, o marcadas como `dicho` si nadie las cuenta.
5. **Qué cuesta**: el tiempo que consume, y si provoca retrabajo.
Y después, la pregunta incómoda que el sistema hace siempre:
- ¿Debería existir esta excepción, o es un paso que existe porque nadie lo borró?
- ¿Si existiera una regla para este caso, dejaría de ser excepción?
- ¿Qué se rompe si la tratamos como regla y la automatizamos?
Ninguna de las tres se contesta desde el escritorio: se contesta con el conteo y con la persona que la atiende.
## Errores que arruinan un plano
- Dibujar el proceso ideal, o el del manual, en lugar del que se caminó.
- Usar el organigrama como si fuera el flujo.
- Promediar: "normalmente se hace así". El plano es de un caso concreto, no del promedio de la memoria.
- Omitir la excepción porque "casi nunca pasa". Casi nunca, multiplicado por volumen, es la fuga.
- No anotar quién empuja el caso entre pasos. Sin eso no se ve por qué avanza cuando hay presión.
- Confundir espera con trabajo, que hace que el diagnóstico culpe a la gente en lugar del diseño.
- Escribir un paso en el plano sin haberlo visto ni tener la cita de quien lo hizo.
## Entregable
`04_plano-real.md` con: el encabezado obligatorio, los casos caminados con su fecha y con quién, el diagrama Mermaid, la tabla de pasos completa, el registro de excepciones con sus cinco datos, los tres contadores y la frase en una línea de qué contradice de lo que el cliente creía.
Y una versión de una página para el cliente, sin jerga y sin el nombre de pila de nadie, que es la que se lleva a la junta.
## Compuerta al cerrar esta fase
- Todos los pasos del flujo principal tienen evidencia `observado` o mejor. Los `dicho` están marcados como tales y listados aparte.
- Cada excepción registrada tiene conteo, o está marcada `dicho` y con el pendiente anotado de quién la cuenta.
- Los tres contadores están calculados con su método declarado.
- El diagrama renderiza y se lee en un teléfono.
- La auditoría del expediente sale en cero.
