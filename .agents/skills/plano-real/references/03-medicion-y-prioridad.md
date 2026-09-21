# Fases 3, medir y priorizar
## Qué se cuenta, y qué no
Se cuenta: pasos, cambios de manos, esperas, excepciones por familia, retrabajos y horas manuales. Nada más.
No se cuenta: sensación, queja, promesa, ni la opinión de nadie sobre qué tan grave es. Eso se anota como `dicho` y se busca el registro.
## Cómo se mide sin comprar nada
El método del sistema es libreta, cronómetro y alguien que mire:
1. Declarar la ventana: tres días, o los casos disponibles, con fechas exactas.
2. Contar sobre los casos que pasaron por la ventana, no sobre un caso recordado.
3. Anotar el dato crudo en `fuentes/`, tal como salió del sistema o de la libreta.
4. Repetir el conteo de un dato clave dos veces: si no cuadra, el dato no está listo.
5. Declarar el método junto al número, siempre. Un número sin método es un `dicho` disfrazado.
## La tabla de la línea base
| Métrica | Valor | Método | Ventana | Fuente | Clase |
|---|---|---|---|---|---|
Las métricas del sistema: pasos totales, cambios de manos, esperas acumuladas (en horas y en días de calendario), excepciones por familia, retrabajos, horas manuales del proceso, casos por mes, y las personas que tocan cada caso.
El costo sale de una multiplicación explícita, nunca de una impresión: `horas manuales por caso × casos por mes × costo hora declarado = costo manual del proceso`. El costo hora lo declara el cliente o sale de nómina con fuente; nunca lo pone el sistema.
## Priorizar con el criterio a la vista
El orden de lo que conviene construir primero sale de cruzar cuatro lecturas del plano:
1. **Dónde se atora**: las esperas acumuladas por paso. Es la fuga que casi nadie ve.
2. **Dónde se pierde**: retrabajos y excepciones frecuentes, con su costo.
3. **Dónde depende de una sola persona**: los puntos de decisión sin criterio escrito. Es el riesgo que el cliente ya sospecha y no ha medido.
4. **Dónde se puede borrar**: pasos sin salida útil, o que existen porque nadie los quitó.
De ahí sale un orden con su razón escrita para cada lugar. Y se cierra con **un solo primer movimiento**, no con una lista de deseos: lo que se hace primero, qué se espera que cambie, y cómo se sabrá.
Reglas de honestidad al priorizar:
- Lo que no se puede comparar contra la línea base no entra como prioridad, entra como deseo.
- El orden no se decide por lo que alguien vendió ni por lo que es más fácil de construir, sino por dónde se atora el trabajo.
- Si dos pasos empatan, gana el que menos gente necesita para sostenerlo.
- Toda prioridad hereda la clase de evidencia más baja de la que depende. Si se sostiene en un `dicho`, se dice.
## Entregables
`05_linea-base.md` con su tabla, su método y su costo calculado, y `06_prioridad.md` con las cuatro lecturas, el orden y el primer movimiento.
La línea base se firma con el cliente: es el punto de comparación de todo el proyecto, y sin firma la mejora del mes doce no se puede demostrar. Quien la firma es quien va a discutir el resultado después, y se anota con fecha.
## Compuerta al cerrar esta fase
- Toda métrica tiene método, ventana y fuente. Cero números huérfanos.
- El costo del proceso está calculado con la fórmula escrita y el costo hora con fuente.
- La línea base está firmada, o queda anotado a quién se le propuso y cuándo.
- Hay un solo primer movimiento, con su criterio y su forma de medirse.
- La auditoría del expediente sale en cero.
