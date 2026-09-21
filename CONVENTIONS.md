# Convenciones: los contratos que comparten todas las fases

Un vocabulario, definido una sola vez. Una fase que inventa sus propios nombres de estado, verbos de bitácora o rutas rompe a las demás en silencio. Cuando escribas o edites cualquier archivo de este sistema, estos contratos mandan sobre la improvisación.

## Las cuatro clases de evidencia, con su forma exacta

Cada afirmación sobre la operación del cliente se escribe con su clase y su recibo, en este formato literal:

`[dicho] "texto textual de la persona" (quién, puesto, cuándo, dónde)`
`[observado] caso <id> caminado de punta a punta con <quién>, el <fecha>`
`[medido] <qué> con método <método>: <fórmula> = <resultado> (fuente: <archivo o registro>)`
`[firmado] <qué> revisado por <quién> el <fecha>`

Reglas de clase: una clase no se promueve sin su recibo. Un `dicho` del dueño no se vuelve `observado` porque otro lo repita. Un `medido` necesita el método declarado, no solo el número: un número sin método es un `dicho` disfrazado. Un `firmado` requiere que el cliente haya visto el documento, no que haya estado de acuerdo en una llamada.
La clase más baja manda: una conclusión que se apoya en tres observaciones y un dicho no es `observado` completa, se escribe con su parte `dicho` marcada.

## Qué se puede hacer con cada clase

| Clase | Se puede | No se puede |
|---|---|---|
| dicho | usar como pista para ir a buscar el caso | entrar a un entregable como hecho, ni sostener una decisión |
| observado | entrar al plano real, describir el paso | borrar el paso ni automatizarlo todavía |
| medido | entrar a la línea base y sostener una prioridad | comparar contra otra medición con método distinto |
| firmado | sostener el rediseño y el compromiso del cliente | usarse como prueba en material público |

## La regla del paso que no se toca

Un paso del proceso no se borra, no se simplifica ni se automatiza si su evidencia es `dicho`. El orden obligatorio es: caminar el caso, escribir el paso en el plano con `[observado]`, y solo entonces proponer el cambio. Si el paso no se pudo observar porque nadie lo ejecutó en la ventana de trabajo, se marca `sin observar` y se pide el caso, no se rellena con lo que se supone.

## Las compuertas entre fases

| Para... | Hace falta antes |
|---|---|
| Entrevistar | Alcance firmado: proceso elegido, quién es quién, permiso del cliente y de la gente |
| Mapear el plano | Casos reales elegidos y al menos uno caminado de punta a punta |
| Medir la línea base | Plano v1 caminado, no dibujado de memoria |
| Priorizar | Línea base contada, con su método declarado |
| Rediseñar | Prioridad con criterio a la vista |
| Construir | Rediseño aprobado por el cliente, por escrito |
| Sostener | Comparación contra la línea base, con el mismo método |

## La forma de negarse

Cuando falta una fase, se dice en una frase qué falta y se hace la primera pregunta que falta. Una frase de por qué, cero sermón. La persona debe sentir que la están entrevistando, nunca que la están regañando.

Ejemplo: "Todavía no puedo levantar el plano: no hay casos reales elegidos. ¿Cuál fue el último caso que atendieron de este tipo, el de la semana pasada?"

## El dedupe

Antes de crear un documento o un caso en el expediente, buscar si ya existe. Si el tema ya vive en otro lado, se actualiza el existente preservando lo anterior con una nota de supersesión y el por qué. Dos verdades vigentes sobre lo mismo es el fracaso que esta regla existe para evitar.

## La compuerta de archivo, obligatoria

Antes de dar por cerrado cualquier artefacto:

1. Correr `python3 scripts/auditar-expediente.py <ruta del expediente> --fase N`.
2. Arreglar lo que salga y volver a correrlo. Un entregable no está terminado hasta que sale en cero.

Comprueba: archivos requeridos por fase, enlaces rotos, entregables sin ninguna observación ni medición, `dicho` sin recibo, excepciones sin conteo, líneas en blanco y guiones largos en los documentos, datos faltantes declarados, y si el brief quedó desactualizado contra el resto del expediente.

## Confidencialidad

Los datos del cliente no salen del expediente. No se citan cifras de cliente en material publicable sin permiso por escrito. Los documentos que se comparten no llevan nombres de pila cuando el puesto basta.
