# Simbolos y reglas del diagrama
Esta es la norma que sigue el generador. Si vas a dibujar un flujo para un cliente con sistema de calidad, esto manda.

## Que exige la ISO 9001, y que no
La ISO 9001:2015 **no impone simbolos ni notacion**. Lo que exige su apartado 4.4 es que la organizacion determine sus procesos, sus entradas y salidas, su secuencia e interaccion, y que **mantenga y conserve informacion documentada** que apoye la operacion y de certeza de que los procesos se ejecutan como se planifico.
Traduccion practica: la norma te obliga a documentar el proceso, no a dibujarlo de cierta forma. Pero cuando se audita, el documento que mas se usa es el flujograma, y el estandar de simbolos al que se recurre es **ISO 5807**, que es el que un auditor reconoce. Dibujar con simbolos propios no incumple, pero obliga a explicar la simbologia cada vez, y eso es friccion gratuita.
Fuentes: ISO 9001:2015 apartado 4.4; ISO 5807:1985 (Information processing, documentation symbols and conventions for data, program and system flowcharts).

## El juego de simbolos ISO 5807, que es el que usamos por defecto
| Forma en el expediente | Simbolo | Se usa para | No se usa para |
|---|---|---|---|
| `inicio` y `fin` | Terminador, ovalo o capsula | Abrir y cerrar el diagrama. Uno de cada uno, siempre | Pasos del proceso: si tiene verbo y alguien lo ejecuta, es actividad |
| `actividad` | Rectangulo | Una operacion o actividad que transforma algo | Documentos ni decisiones |
| `decision` | Rombo | Una pregunta que abre caminos. La condicion se escribe dentro o en la salida | Cualquier paso con dos salidas que en realidad no son excluyentes |
| `documento` | Rectangulo con el borde inferior ondulado | Un documento o registro que entra o sale: una hoja, un formato, un pdf firmado | Un sistema o una base de datos |
| `datos` | Paralelogramo | Entrada o salida de informacion: un dato que se captura o se consulta | Un formato impreso, que es documento |
| `entrada-manual` | Trapecio con la parte superior inclinada | Cuando una persona teclea o transcribe el dato a mano | Una captura automatica, que es datos |
| `demora` | Forma de D, con el lado curvo a la derecha | El caso que espera y nadie lo trabaja: la espera entre dos pasos | Trabajo que se esta haciendo |
| `base-de-datos` | Cilindro | Un sistema donde vive la informacion y se consulta | Un archivo suelto o una hoja de calculo, que son documento |
| `almacenamiento` | Triangulo invertido | Un archivo o resguardo del que no se vuelve a leer en el flujo | Un sistema activo |
| `preparacion` | Hexagono alargado | Una preparacion previa: inicializar, configurar, armar el expediente antes de empezar | Un paso del proceso |
| `subproceso` | Rectangulo con doble barra vertical a los lados | Un proceso ya detallado en otro diagrama | Un paso simple |
| `conector` | Circulo con una letra | Continuar el flujo en otra hoja o en otra parte del mismo diagrama | Adorno: si el diagrama cabe, no hace falta |
Reglas de flujo que acompanan los simbolos:
- La direccion por defecto es de arriba hacia abajo. Si una linea va en otro sentido, lleva punta de flecha; si va hacia abajo o a la derecha, no hace falta.
- Un solo inicio y un solo fin. Si hay dos salidas reales, se documentan como dos procesos.
- Las lineas se cruzan lo menos posible. Antes de cruzar, se reorganiza.
- Un conector se usa cuando el diagrama se parte por hoja, no para esconder un salto.

## El otro juego: el cursograma analitico (OTIDA)
En el analisis de operaciones y en la ingenieria de metodos se usa otro juego, con cinco actividades: Operacion, Transporte, Inspeccion, Demora y Almacenamiento. **Las formas no son las mismas que las del flujograma ISO 5807**, y confundirlos es el error clasico: en el cursograma la operacion es un circulo y la inspeccion un cuadrado, mientras que en el flujograma el proceso es un rectangulo y no existe el cuadrado de inspeccion.
Cuando un cliente pide un cursograma (tipico cuando pesa el area de produccion o de metodos), se cambia el juego con la opcion `--set cursograma` del generador, que dibuja: `operacion` como circulo, `inspeccion` como cuadrado, `transporte` como flecha ancha, `demora` como D y `almacenamiento` como triangulo.
Fuente: practica documentada del cursograma analitico en ingenieria de metodos y su uso en el analisis del proceso de flujo.

## La espera no se escribe: se dibuja
El hallazgo de casi todos los diagnosticos vive en las esperas, no en el trabajo. Por eso el generador **inserta un simbolo de demora entre dos pasos cada vez que la tabla declara una espera**, con el tiempo adentro. Si el caso espera cuatro horas entre el paso 2 y el 3, se ve cuatro horas de D entre esos dos rectangulos. Un dato en una columna se lee; una fila de demoras se entiende.
El resumen del cursograma clasico, con la cuenta por tipo de actividad y el tiempo total, se agrega al pie del entregable: cuantas operaciones, cuantas demoras, cuantas inspecciones, y cuantas horas de cada una. Ese cuadro es el que convence en la junta.

## Que se dibuja a un lado, y por que
- **Carril izquierdo: quien lo hace.** Puesto, no nombre de pila. Cuando el dueño cambia, cambia el carril: esa es la lectura de cuantas veces el caso cambia de manos, que es el primer numero del plano.
- **Columna derecha: las rutas de excepcion.** Cada excepcion sale de su paso con linea punteada hacia una caja con su familia y su ruta. No se dibujan como nota al pie, porque una excepcion es una ruta que alguien atiende, no un comentario.
- **Certeza visible.** Lo observado, medido o firmado va en linea solida. Lo que solo se dijo, o que nadie vio ejecutar, va en gris punteado. El dibujo nunca afirma mas que la evidencia.
- **Una sola columna principal, y se pagina.** El diagrama no se estira hasta hacerse ilegible: cuando el proceso no cabe con aire en una hoja, se corta y se une con el simbolo de conector (A, B, C), que es exactamente para lo que existe. El generador corta solo, cada siete elementos por hoja, y numera las hojas.

## Las cuatro clases de ruta

El tipo de una ruta no es decoración: cambia el trazo y cambia el significado.

| tipo | trazo | qué significa |
|---|---|---|
| `normal` | línea sólida negra | el camino que el caso sigue cuando todo sale bien |
| `excepcion` | punteada naranja | el caso se desvía porque algo no se cumplió |
| `retrabajo` | punteada azul, por el carril exterior | el camino vuelve a un paso anterior. Es el que se cobra dos veces |
| `rechazo` | punteada roja corta | el caso se cierra sin continuar. Es un final, no una pausa |

Una decisión sin dos salidas etiquetadas no está documentada: está dibujada.

## Lo que el generador verifica solo
- Que no haya dos formas encimadas: si el acomodo produce un traslape, lo reporta y no entrega.
- Que el diagrama de la nota corresponda a la tabla: si la tabla cambio y no se regenero, la auditoria del expediente lo marca como vencido.
- Que cada forma exista en el juego de simbolos declarado: una forma desconocida se reporta en vez de dibujarse como rectangulo sin avisar.

## Fuentes
- ISO 9001:2015, apartado 4.4 Sistema de gestion de la calidad y sus procesos, y 7.5 Informacion documentada.
- ISO 5807:1985, Documentation symbols and conventions for data, program and system flowcharts.
- Practica documentada del cursograma analitico (OTIDA) en ingenieria de metodos.
