# Changelog

Los cambios notables de `/plano-real` se registran aquí. Versionado semántico:

- **MAJOR:** un contrato del expediente o del flujo cambia de forma incompatible y necesita migración deliberada.
- **MINOR:** capacidad nueva o mejora de contrato compatible hacia atrás.
- **PATCH:** correcciones compatibles de comportamiento, documentación o empaquetado.

## 0.5.0

El diagrama deja de ser una columna. Ahora es un grafo con ramas de verdad.

### Impacto

- **El modelo cambia: dos tablas, no una lista.** `Nodos` (id, texto, forma, quién, sistema, trabajo, espera, evidencia) y `Rutas` (desde, hacia, etiqueta, tipo). Una lista no puede representar un grafo: por eso el dibujo salía lineal aunque el proceso tuviera caminos alternos. Esta era la causa de raíz, no el estilo.
- **Acomodo por capas.** El generador calcula el rango de cada nodo por camino más largo, ordena los nodos de cada capa, y dibuja el grafo: los caminos se separan en el rombo y se vuelven a juntar donde corresponde.
- **Cuatro clases de ruta con trazo propio.** `normal` sólida, `excepcion` punteada naranja, `retrabajo` punteada azul por el carril exterior, `rechazo` punteada roja corta y terminal.
- **Los retrabajos salen por el carril exterior** y entran al paso destino por arriba, para no cruzar ninguna forma.
- **Un rombo sin dos salidas ya no pasa.** El diagnóstico cuenta las decisiones y avisa cuántas tienen dos o más salidas.
- **Rutas que cruzan de hoja** se unen con el símbolo de conector, con la letra de la hoja destino.
- El ejemplo cambia: ahora es el control de la documentación, con una decisión de tres salidas, tres retrabajos, una ruta de excepción y un cierre terminal por rechazo.

### Compatibilidad

- La tabla vieja de pasos sigue funcionando: el generador la convierte en nodos y rutas, con la cadena como camino principal y cada excepción como nodo con su ida y su regreso.
- El bloque Mermaid de las notas anteriores cambia; volver a generar lo actualiza.

### Actualizacion

- Volver a instalar y regenerar.

### Migracion

- Ninguna obligatoria. Para aprovechar las ramas, migrar la tabla de pasos a las tablas de nodos y rutas.

### Entrega

- Verificación con el ejemplo: 17 nodos, 20 rutas, 4 decisiones y las 4 con dos o más salidas, 3 retrabajos, 0 formas encimadas, 0 rutas que atraviesan una forma.

## 0.4.0

Ramas con condicion, retrabajo visible y la ficha del proceso que pide ISO 9001.

### Impacto

- **Ramas etiquetadas.** Cada decision puede declarar su `condicion`, que se escribe sobre la ruta que sale del rombo. Antes el rombo abria caminos sin decir con que criterio.
- **Retrabajo visible.** La columna `regreso` declara a que paso vuelve la excepcion, y la caja lo dice: "vuelve al paso N". Sin eso, una excepcion parecia un callejon sin salida.
- **La etiqueta de sistema de un rombo queda adentro.** Antes se dibujaba debajo y parecia una etiqueta de la flecha. El espacio de abajo ahora es para la condicion.
- **Ficha del proceso.** Si la nota declara entradas, salidas, secuencia, criterios, recursos, responsables, riesgos y mejora, el entregable trae una tabla que mapea cada campo al requisito 4.4.1 de ISO 9001:2015, con su letra.
- Leyenda de rutas en el pie: linea solida camino normal, punteada naranja ruta de excepcion, y "vuelve al paso N" retrabajo.

### Compatibilidad

- Las columnas nuevas son opcionales. Sin `condicion` ni `regreso`, el diagrama se dibuja como antes.

### Actualizacion

- Volver a instalar y regenerar.

### Migracion

- Ninguna.

### Entrega

- Ejemplo regenerado: 6 rutas de excepcion con su condicion, 6 retrabajos declarados, ficha de proceso en ocho campos, cero traslapes.

## 0.3.0

El diagrama se pagina y respira. Adios a las partes amontonadas.

### Impacto

- **Paginacion con conectores.** Cada hoja lleva siete elementos como maximo, con el simbolo de conector (A, B, C) para pasar de una a otra, que es el uso para el que existe. Un proceso de diez pasos sale en dos hojas legibles en lugar de una columna interminable.
- **Mas aire.** El hueco minimo entre formas pasa de 14 a 22 unidades y las etiquetas de sistema quedan a 14 unidades del borde inferior de su forma, en lugar de 9.
- **El rombo ya no tira su etiqueta afuera.** La etiqueta de sistema de una decision se dibuja centrada debajo del rombo, con su propio espacio reservado.
- **La flecha de excepcion arranca con aire:** sale diez unidades a la derecha de la forma, no pegada a su borde.
- Cada hoja lleva su titulo y, cuando hay mas de una, su numero. En impresion cada hoja empieza en pagina nueva.

### Compatibilidad

- La tabla de pasos no cambia. Cambia el acomodo del dibujo.

### Actualizacion

- Volver a instalar y regenerar.

### Migracion

- Ninguna.

### Entrega

- Verificacion con el ejemplo: dos hojas, cero traslapes, hueco minimo de 22 unidades, cero textos fuera de su caja.

## 0.2.1

Margenes de texto conservadores, para que ninguna etiqueta toque el borde de su forma.

### Impacto

- El ancho de linea de cada simbolo se recorta segun la forma: el paralelogramo y el trapecio pierden ancho por el sesgo, y el rombo solo tiene el centro util.
- La etiqueta del carril se recorta a 22 caracteres para que no invada el margen izquierdo.
- Verificacion geometrica agregada: se revisa que ningun texto se salga del lienzo ni de su forma.

### Compatibilidad

- Compatible. Solo cambia el corte de linea de las etiquetas.

### Actualizacion

- Volver a instalar y regenerar el diagrama.

### Migracion

- Ninguna.

### Entrega

- Ejemplo regenerado: 58 textos, ninguno fuera de su caja, cero traslapes.

## 0.2.0

El diagrama pasa a los simbolos de ISO 5807 y se dibuja en vertical, como se lee un flujograma.

### Impacto

- Simbolos correctos, no cajas genericas: terminador para inicio y fin, rectangulo para actividad, rombo para decision, documento con el borde ondulado para registros, paralelogramo para datos, cilindro para sistemas y forma de D para la demora.
- El juego del cursograma OTIDA queda disponible con `--set cursograma`: circulo para operacion, cuadrado para inspeccion, flecha ancha para transporte.
- La espera deja de ser una columna y se vuelve un simbolo: el generador inserta una demora entre dos pasos cada vez que la tabla declara espera, con el tiempo adentro. Diez esperas y 116 horas se ven de un golpe.
- Acomodo vertical con carril de puestos a la izquierda y rutas de excepcion a la derecha. Cada cambio de dueno se ve en el carril.
- El generador se autoinspecciona: si el acomodo produce formas encimadas, lo reporta y no entrega. Estado actual del ejemplo: cero traslapes.
- Nueva referencia `references/06-simbolos-y-normas.md` con que exige ISO 9001, el juego completo de ISO 5807, el del cursograma y las reglas de flujo.

### Compatibilidad

- La tabla de pasos gana una columna opcional `forma`. Sin ella, el generador deduce la forma del tipo de paso y del juego de simbolos, asi que las tablas viejas siguen funcionando.
- El bloque Mermaid de las notas anteriores cambia; volver a generar lo actualiza.

### Actualizacion

- Volver a instalar y regenerar el diagrama de las notas existentes.

### Migracion

- Ninguna sobre datos de cliente.

### Entrega

- Ejemplo regenerado en `examples/` con las formas declaradas, y verificacion de traslapes en cero.

## 0.1.1

El diagrama del plano deja de ser un dibujo y se vuelve un derivado de la tabla de pasos.

### Impacto

- Nuevo script `generar-diagrama.py`: lee la tabla de pasos del expediente y escribe el diagrama Mermaid dentro de la nota, además del entregable de una página en HTML con la marca, listo para imprimir.
- El dibujo lleva la verdad a la vista: los pasos observados, medidos o firmados van en línea sólida, y los que solo se dijeron, en gris punteado. Los romanos de la excepción van como ruta aparte.
- Contadores automáticos: pasos, puntos de decisión y esperas acumuladas, sumadas desde la propia tabla.
- La auditoría del expediente gana un chequeo: si la tabla de pasos cambió y el diagrama no se regeneró, marca `diagrama_vencido` y el entregable no se puede cerrar.
- Ejemplo completo en `examples/`, con expediente y entregable renderizado.

### Compatibilidad

- Compatible hacia atrás. El script de auditoría sigue funcionando igual y el chequeo nuevo solo aplica cuando la nota tiene el bloque de diagrama marcado.

### Actualización

- Volver a instalar el plugin o el marketplace según la ruta que uses. No hay nada que migrar.

### Migración

- Ninguna.

### Entrega

- Probado de punta a punta: generar, verificar que está al día, editar solo la tabla y comprobar que tanto `generar-diagrama.py --check` como la auditoría lo detectan, y regenerar.

## 0.1.0

Primera versión pública del método, empaquetado como skill instalable.

### Impacto

- Seis fases con compuerta: arranque, entrevistas, plano real, medición y prioridad, rediseño y prueba, sostenimiento.
- Cuatro clases de evidencia con lo que cada una permite y prohíbe, y la regla de que no se rediseña lo que no se observó.
- Barrido de excepciones en siete familias, con sus cinco datos y sus tres preguntas obligatorias.
- Auditores de expediente ejecutables, que condicionan el cierre de cada entregable.

### Compatibilidad

- Nuevo. No hay versiones anteriores ni migración.
- Instalable en Claude Code vía plugin, en Codex/ChatGPT vía marketplace de Codex o por petición directa en un chat, y en Hermes por petición al agente.

### Actualización

- Nada que hacer. Primera versión.

### Migración

- Ninguna.

### Entrega

- El árbol canónico es `.agents/skills/plano-real/`. Los manifiestos de instalación de cada arnés viven en `.claude-plugin/`, `.codex-plugin/` y `.agents/plugins/`.
- Probado el script de auditoría contra tres expedientes de prueba: uno limpio en cero, uno roto con seis fallas, y uno con un `dicho` sin recibo.
