# Fase 4, rediseñar y probar
## El orden del rediseño, y no se invierte
**Borrar, simplificar, conectar, automatizar.** En ese orden. La regla que lo protege: un paso menos por semana antes de automatizar cualquier paso. Automatizar lo que no se entiende no acelera el trabajo, acelera el error.
## Qué se hace en cada movimiento
**Borrar.** Pasos sin salida útil, aprobaciones sin decisión real, registros que nadie lee, copias que se hacen por costumbre. Criterio: si nadie extrañó el paso en la última semana, se prueba quitarlo. Y toda prueba de borrado tiene su fecha y su resultado: qué se rompió, o que no se rompió nada, que también es el dato.
**Simplificar.** Un formato en lugar de tres, un criterio en lugar de un juicio por caso, un umbral escrito en lugar de preguntar siempre al jefe.
**Conectar.** Que el estado de un caso viva en un solo lugar y que el aviso al siguiente salga del sistema, no de que alguien se acuerde. Un caso, un lugar, un estado, un dueño, un aviso.
**Automatizar.** Solo lo que ya está entendido, borrado y conectado, y solo lo que cumple una de tres condiciones: es repetitivo, es propenso a error humano, o es una espera que se puede eliminar.
## Las excepciones se diseñan, no se ignoran
Cada excepción del registro recibe una decisión explícita, ninguna se queda sin resolver:
1. **Se borra**: no debería existir, y se prueba quitarla.
2. **Se vuelve regla**: el caso dejó de ser excepción y se documenta como parte del flujo.
3. **Se autoriza por umbral**: hasta cierto monto o riesgo la resuelve una persona con criterio escrito; arriba de eso, sube.
4. **Se queda humana a propósito**: requiere juicio, relación o responsabilidad, y se escribe el criterio de quién decide y con qué información.
Y lo que nunca se automatiza en esta casa: lo que toca dinero sin revisión, lo que toca una promesa al cliente sin criterio, lo que toca la relación con una persona, y lo que nadie entiende todavía.
## El proceso nuevo, escrito como proceso
`07_rediseno.md` con: el flujo nuevo en Mermaid, la tabla de pasos con dueño por etapa, estado visible y aviso al siguiente, la tabla de excepciones con su decisión, la lista explícita de lo que se borró y lo que se dejó manual con su razón, y qué pasa con la gente que hacía lo que desaparece.
Aprobación: el cliente aprueba por escrito antes de construir. Un rediseño que no está aprobado no se implementa, aunque parezca obvio.
## Probar contra la línea base, con el mismo método
`08_prueba.md` con:
- Los casos de prueba, que son reales: uno del caso frecuente, uno de una variante distinta, uno con excepción y uno urgente.
- El criterio de aceptación **escrito antes de construir**, no después de ver el resultado.
- La comparación contra la línea base, con el mismo método y la misma ventana, y su diferencia expresada en los mismos números: pasos, manos, esperas, retrabajos, horas manuales.
- Lo que salió distinto de lo esperado, dicho sin adornos.
Regla anti-humo: si el resultado no se puede comparar contra la línea base con el mismo método, no es una mejora, es un cambio.
## Quién ejecuta qué
En el diseño queda escrito qué puede ejecutar el software solo, qué puede resolver un agente con la información disponible, y qué tiene que decidir una persona. Y el nivel de revisión por riesgo: lo barato se automatiza, lo caro se revisa.
## Compuerta al cerrar esta fase
- El rediseño está aprobado por escrito.
- Cada excepción del registro tiene su decisión tomada.
- El criterio de aceptación existía antes de construir.
- La prueba se comparó contra la línea base con el mismo método, o se dice por qué no se pudo.
- Quedó anotado qué se rompió en las pruebas de borrado, incluso cuando la respuesta es nada.
- La auditoría del expediente sale en cero.
