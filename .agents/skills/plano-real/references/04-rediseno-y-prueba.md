# Fase 4, rediseñar y probar
## Objetivo
Diseñar el primer cambio priorizado y probarlo contra la línea base sin eliminar controles ni ejecutar sin autorización.
## Qué necesita para empezar
Leer [las convenciones](00-convenciones.md). Prioridad justificada, evidencia del tramo y línea base con método. Para construir o probar en operación: aprobación escrita de la versión, criterio de aceptación previo y plan de reversión o autorización específica de irreversibilidad.
## Pasos de trabajo
1. Evaluar eliminar, simplificar, conectar y automatizar; resolver excepciones y responsabilidades. **Termina cuando:** el diseño declara qué cambia, qué se conserva, riesgos y responsables.
2. Escribir aceptación y reversión; presentar la versión y obtener aprobación. **Termina cuando:** hay recibo de la versión autorizada; si no, detener construcción y pruebas operativas.
3. Ejecutar los casos autorizados y comparar con el método de la línea base. **Termina cuando:** resultados, incidentes y limitaciones están registrados, sin anunciar mejora donde no puede comprobarse.
### El orden del rediseño, y no se invierte
**Evaluar borrar, simplificar, conectar y automatizar.** En ese orden, sin cuota de eliminación. Justificar qué se elimina y qué debe conservarse como control. Automatizar lo que no se entiende no acelera el trabajo, acelera el error.
### Qué se hace en cada movimiento
**Borrar.** Pasos sin salida útil, aprobaciones sin decisión real, registros que nadie lee, copias que se hacen por costumbre. Antes de probar: documentar función, riesgo cubierto, obligación legal o contractual, dependencias, responsable que autoriza, señal de detención y procedimiento de reversión. Que nadie lo haya extrañado no demuestra que sea innecesario. Un control poco frecuente puede ser indispensable. Y toda prueba de borrado tiene su fecha y su resultado: qué se rompió, o que no se rompió nada, que también es el dato.
**Simplificar.** Un formato en lugar de tres, un criterio en lugar de un juicio por caso, un umbral escrito en lugar de preguntar siempre al jefe.
**Conectar.** Que el estado de un caso viva en un solo lugar y que el aviso al siguiente salga del sistema, no de que alguien se acuerde. Un caso, un lugar, un estado, un dueño, un aviso.
**Automatizar.** Solo lo que ya está entendido, evaluado para simplificación y conectado, y solo lo que cumple una de tres condiciones: es repetitivo, es propenso a error humano, o es una espera que se puede eliminar.
### Las excepciones se diseñan, no se ignoran
Cada excepción del registro recibe una decisión explícita, ninguna se queda sin resolver:
1. **Se borra**: no debería existir, y se prueba quitarla.
2. **Se vuelve regla**: el caso dejó de ser excepción y se documenta como parte del flujo.
3. **Se autoriza por umbral**: hasta cierto monto o riesgo la resuelve una persona con criterio escrito; arriba de eso, sube.
4. **Se queda humana a propósito**: requiere juicio, relación o responsabilidad, y se escribe el criterio de quién decide y con qué información.
Y lo que nunca se automatiza en esta casa: lo que toca dinero sin revisión, lo que toca una promesa al cliente sin criterio, lo que toca la relación con una persona, y lo que nadie entiende todavía.
### El proceso nuevo, escrito como proceso
`07_rediseno.md` con: el flujo nuevo en Mermaid, la tabla de pasos con dueño por etapa, estado visible y aviso al siguiente, la tabla de excepciones con su decisión, la lista explícita de lo que se borró y lo que se dejó manual con su razón, y qué pasa con la gente que hacía lo que desaparece.
Aprobación: el cliente aprueba por escrito la versión identificada del rediseño antes de construir, con el recibo `[aprobado]` definido en las convenciones. Un rediseño que no está aprobado no se implementa, aunque parezca obvio.
### Probar contra la línea base, con el mismo método
`08_prueba.md` con:
- Los casos de prueba, que son reales: uno del caso frecuente, uno de una variante distinta, uno con excepción y uno urgente.
- El criterio de aceptación **escrito antes de construir**, no después de ver el resultado.
- El plan de reversión: estado anterior recuperable, responsable, señales de detención y comprobación de recuperación. No ejecutar pruebas irreversibles sin autorización específica.
- La comparación contra la línea base, con el mismo método y la misma ventana, y su diferencia expresada en los mismos números: pasos, manos, esperas, retrabajos, horas manuales.
- Lo que salió distinto de lo esperado, dicho sin adornos.
Regla anti-humo: si el resultado no se puede comparar contra la línea base con el mismo método, no es una mejora, es un cambio.
### Quién ejecuta qué
En el diseño queda escrito qué puede ejecutar el software solo, qué puede resolver un agente con la información disponible, y qué tiene que decidir una persona. El nivel de revisión depende de impacto, reversibilidad, sensibilidad de datos y obligaciones, no solo del costo: una acción barata puede tener consecuencias graves.
## Si falta evidencia
Sin aprobación de versión no construir. Sin evidencia del tramo, volver al levantamiento. Sin comparación válida, informar cambio no verificado y la razón; sin autorización o reversión suficiente, no ejecutar la prueba operativa.
## Archivos que produce o actualiza
Actualizar `07_rediseno.md` y `08_prueba.md` con los contenidos descritos arriba, los recibos en `fuentes/` y el estado en `00_AGENT_BRIEF.md`.
## Termina cuando
- El rediseño está aprobado por escrito.
- Cada excepción del registro tiene su decisión tomada.
- El criterio de aceptación existía antes de construir.
- La prueba se comparó contra la línea base con el mismo método, o se dice por qué no se pudo.
- Quedó anotado qué se rompió en las pruebas de borrado, incluso cuando la respuesta es nada.
- Cada cambio probado tiene evaluación de riesgo, autorización y reversión verificable, o una autorización específica de irreversibilidad. No se eliminó un paso solo para cumplir una cuota.
- La auditoría del expediente sale en cero.
## Entrega al siguiente paso
Entregar a fase 5 la versión implementada, resultados frente a la línea base, incidentes, limitaciones, reversión y responsables de lo que queda manual. No trasladar una hipótesis de mejora como resultado comprobado.
Actualizar el brief y cerrar en el chat con resultado, sustento, archivo, pendiente y siguiente movimiento según [la guía principal](../SKILL.md).
