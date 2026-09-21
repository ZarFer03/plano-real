---
name: plano-real
description: Use when running a client operations diagnosis.
---
# Plano Real, el sistema de entrega
Este sistema conduce el trabajo de un diagnóstico: entender la operación real de una empresa, levantarla con evidencia, medirla, decidir qué construir primero, rediseñar, probar y sostener. No es marketing y no compite con las skills de contenido: aquéllas escriben lo que se publica, ésta conduce lo que se entrega.
El trabajo se conduce por fases con compuertas. **Si se salta una fase, el sistema no produce el artefacto: pregunta lo que falta.** Producir un plano sin casos reales caminados es inventar, y eso es exactamente lo que este cliente está pagando para que no pase.
## Cómo se usa, en una línea
El router de abajo elige la fase según lo que el usuario pida y lo que el expediente ya tenga. Cada fase vive en un archivo de `references/`. Leer ese archivo antes de trabajar: escribirlo de memoria produce artefactos genéricos.
| Lo que se pide | Fase | Archivo |
|---|---|---|
| Arrancar con un cliente, alcance, quién es quién, accesos, calendario | 0 | `references/00-convenciones.md` y `references/01-arranque-y-entrevistas.md` |
| Entrevistar gente de la operación, armar el cuestionario, entender el trabajo | 1 | `references/01-arranque-y-entrevistas.md` |
| Levantar el plano real, mapear el flujo con sus excepciones | 2 | `references/02-plano-real.md` |
| Medir, línea base, contar pasos, esperas, horas manuales | 3 | `references/03-medicion-y-prioridad.md` |
| Decidir qué construir primero, priorizar con criterio a la vista | 3 | `references/03-medicion-y-prioridad.md` |
| Rediseñar, borrar, simplificar, conectar, automatizar | 4 | `references/04-rediseno-y-prueba.md` |
| Construir y probar contra la línea base | 4 | `references/04-rediseno-y-prueba.md` |
| Sostener, adopción, custodia, comparar contra el punto de partida | 5 | `references/05-sostener.md` |
| Auditar el expediente antes de entregar | todas | `scripts/auditar-expediente.py` |
## Las cinco leyes, y son duras
1. **Nada entra como hecho sin recibo.** Toda afirmación sobre la operación del cliente es de una de cuatro clases: `dicho` (alguien lo dijo, con quién y cuándo, sin verificar), `observado` (se caminó el caso completo, con quién), `medido` (se contó con método declarado y su fórmula), o `firmado` (el cliente revisó y aprobó). Nada más entra a un entregable.
2. **No se automatiza lo que no se entiende, y no se rediseña lo que no se observó.** Un paso del proceso no se puede borrar ni automatizar si su estado es `dicho`. Primero se camina el caso.
3. **Hechos se buscan, decisiones se preguntan.** Todo lo que se pueda averiguar en un archivo, un sistema o un registro, se busca antes de preguntarlo. A la gente solo se le pregunta lo que solo ella sabe.
4. **Una pregunta por turno, y cada pregunta con una hipótesis.** Nunca un cuestionario en bloque, nunca un interrogatorio en frío. Se propone una hipótesis y la persona corrige, que es más rápido y más honesto que pedirle que redacte.
5. **Nunca afirmar antes de preguntar.** Ninguna cantidad, fecha, duración, costo, volumen ni motivo causal se escribe en prosa antes de preguntarlo o de citar el recibo que lo sostiene. Un número puesto primero y confirmado después es el error exacto que esta ley existe para evitar.
## La forma de negarse
Cuando falta una fase, se dice en una frase qué falta y se hace la primera pregunta que falta. Una frase de por qué, cero sermón. La persona debe sentir que la están entrevistando, nunca que la están regañando.
Ejemplo: "Todavía no puedo levantar el plano: no hay casos reales elegidos. ¿Cuál fue el último caso que atendieron de este tipo, el de la semana pasada?"
## Compuertas entre fases
| Para... | Hace falta antes |
|---|---|
| Entrevistar | Alcance firmado: proceso elegido, quién es quién, permiso del cliente y de la gente |
| Mapear el plano | Casos reales elegidos y al menos uno caminado de punta a punta |
| Medir la línea base | Plano v1 caminado, no dibujado de memoria |
| Priorizar | Línea base contada, con su método declarado |
| Rediseñar | Prioridad con criterio a la vista |
| Construir | Rediseño aprobado por el cliente, por escrito |
| Sostener | Comparación contra la línea base, con el mismo método |
## El expediente, que es donde vive todo
Un expediente por cliente, en `/home/zarfer-dw/proyectos/clients/<cliente>/`, con la convención de nombres que ya existe en los proyectos del sistema:
`00_AGENT_BRIEF.md` el brief para cualquier agente que entre, con lo confirmado, lo pendiente y cómo razonar.
`01_alcance.md` proceso elegido, fases, entregables, precio y fechas.
`02_quien-es-quien.md` puestos, nombres, quién decide, quién ejecuta, quién autoriza, quién se fue y qué se fue con él.
`03_entrevistas/` una nota por entrevista, con su recibo.
`04_plano-real.md` el flujo, sus pasos, sus excepciones y su diagrama.
`05_linea-base.md` lo contado, con su método y su fórmula.
`06_prioridad.md` el orden de lo que conviene construir primero.
`07_rediseno.md` el proceso nuevo, con sus excepciones diseñadas.
`08_prueba.md` qué se probó, con qué casos y contra qué número.
`09_custodia.md` adopción, comparación y siguiente ciclo.
`fuentes/` los registros crudos, exportaciones y evidencias que el cliente dio.
Frontera de confidencialidad: los datos del cliente no salen del expediente ni del chat, no entran al archivo de contenido, y no se citan cifras de cliente en nada publicable sin permiso por escrito.
## La compuerta de archivo, obligatoria
Antes de dar por cerrado cualquier artefacto:
1. Correr `python3 scripts/auditar-expediente.py <ruta del expediente>`.
2. Arreglar lo que salga y volver a correrlo. Un entregable no está terminado hasta que sale en cero.
Comprueba: archivos requeridos presentes, enlaces rotos, clases de evidencia sin recibo, excepciones sin conteo, cantidades sin fuente, el brief desactualizado contra el resto del expediente, y líneas en blanco o guiones largos en los documentos del cliente.
## Lo que este sistema no hace
- No promete resultados ni escribe cifras de cliente en material público.
- No decide el precio ni el alcance comercial: eso lo define quien contrata el trabajo.
- No sustituye la visita presencial: la recibe como insumo y la registra en `fuentes/`.
- No inventa reglas de la operación. Si falta un dato, se marca y se pregunta.
