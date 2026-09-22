# Convenciones del expediente de operaciones
Se lee antes de trabajar en cualquier fase. Es el contrato compartido del sistema.
## Evidencia y aprobación son independientes
Cada afirmación sobre la operación del cliente se escribe con su clase y su recibo, en este formato literal:
`[dicho] "texto textual de la persona" (quién, puesto, cuándo, dónde)`
`[observado] caso <id> caminado de punta a punta con <quién>, el <fecha>`
`[medido] <qué> con método <método>: <fórmula> = <resultado> (fuente: <archivo o registro>)`
La evidencia tiene tres clases: `dicho`, `observado` y `medido`. La aprobación se registra aparte:
`[aprobado] <documento> versión <id> aprobado por <responsable> el <AAAA-MM-DD> (fuente: <ruta local del recibo>)`
La versión identifica el documento que el cliente realmente aprobó; si cambia el contenido autorizado se necesita nueva aprobación. Conservar el recibo en el expediente y verificar su alcance, autoría y correspondencia con la versión. El auditor comprueba formato y existencia, no autenticidad.
Compatibilidad: `[firmado]` se conserva como registro histórico con aviso; no cuenta como evidencia ni autoriza una versión nueva. Migrar solo desde recibos disponibles, sin inventar versión o aprobación. En tablas del plano, la celda evidencia inicia con `[dicho]`, `[observado]` o `[medido]`; las aprobaciones viven aparte. Etiquetas sueltas o lenguaje natural no sustituyen recibos.
Reglas de clase: una clase no se promueve sin su recibo. Un `dicho` del dueño no se vuelve `observado` porque otro lo repita. Un `medido` necesita el método declarado, no solo el número: un número sin método es un `dicho` disfrazado. Una aprobación no convierte un dicho en observación ni una observación en medición.
La clase más baja manda: una conclusión que se apoya en tres observaciones y un dicho no es `observado` completa, se escribe con su parte `dicho` marcada.
## Qué se puede hacer con cada clase
| Clase | Se puede | No se puede |
|---|---|---|
| dicho | usar como pista para ir a buscar el caso | entrar a un entregable como hecho, ni sostener una decisión |
| observado | entrar al plano real, describir el paso | borrar el paso ni automatizarlo todavía |
| medido | entrar a la línea base y sostener una prioridad | comparar contra otra medición con método distinto |
| aprobación (no evidencia) | autorizar el alcance de una versión con recibo | sustituir observación, medición o permiso de publicación |
## La regla del paso que no se toca
Un paso del proceso no se borra, no se simplifica ni se automatiza si su evidencia es `dicho`. El orden obligatorio es: caminar el caso, escribir el paso en el plano con `[observado]`, y solo entonces proponer el cambio. Si el paso no se pudo observar porque nadie lo ejecutó en la ventana de trabajo, se marca `sin observar` y se pide el caso, no se rellena con lo que se supone.
## Compuertas y avance acotado
| Para | Hace falta antes |
|---|---|
| Entrevistar | Alcance aprobado, proceso elegido, responsables y permisos |
| Mapear | Casos elegidos y al menos uno caminado de punta a punta |
| Medir | Plano caminado para el tramo medido |
| Priorizar | Línea base con método, fuente y limitaciones |
| Rediseñar | Prioridad justificada y evidencia del tramo afectado |
| Construir | Versión del rediseño aprobada por escrito |
| Sostener | Comparación válida contra la línea base, o limitación explícita sin afirmar mejora |
Los estados del documento son `borrador`, `listo para revisión` y `aprobado para ejecutar`. No son clases de evidencia. Un borrador puede mostrar zonas desconocidas marcadas; no puede presentarlas como hechos ni autorizar cambios sobre ellas.
Un pendiente bloquea la decisión que depende de él. Se puede avanzar en un tramo independiente solo si quedan documentados alcance, dependencias, límites y riesgos compartidos; si afecta seguridad, dinero, cumplimiento o una dependencia del tramo, no es independiente. El cierre de la fase completa sigue exigiendo sus compuertas y la auditoría completa. No existe un modo de auditoría parcial que apruebe todo el expediente.
Cuando falta un requisito, explicar cuál y pedir el primer dato faltante, sin completar con supuestos.
## El barrido de excepciones, que es donde se esconde el trabajo real
Cada paso del plano lleva su columna de excepción. Una excepción no es ruido: es una ruta que existe y que alguien atiende. Las siete familias, con su pregunta de disparo:
1. **Por dato faltante.** ¿Qué pasa cuando el dato no está o está mal? (el campo vacío, el número mal capturado, el archivo que no llegó)
2. **Por autorización.** ¿Qué pasa cuando el monto, el riesgo o el cliente exige permiso de alguien más?
3. **Por tipo de caso.** ¿Qué pasa cuando el caso es de un cliente o una variante que no sigue la regla?
4. **Por tiempo.** ¿Qué pasa cuando es urgente, o cuando llega fuera de horario?
5. **Por capacidad.** ¿Qué pasa cuando no hay quién lo haga?
6. **Por sistema.** ¿Qué pasa cuando la herramienta no lo permite?
7. **Por decisión humana.** ¿Qué pasa cuando alguien tiene que juzgar algo que no está escrito?
Cada excepción se registra con: cuántas veces pasa (conteo o rango con fuente), quién la resuelve, cuánto cuesta en tiempo, y la pregunta incómoda obligatoria: ¿debería existir, o es un paso que existe porque nadie lo borró?
Regla de oro: si una excepción no tiene conteo, su estado es `dicho` y no puede sostener un rediseño. Se cuenta antes de tocarla.
## Convenciones de escritura de los entregables
- Todo entregable se escribe en español de México, en el idioma del cliente, sin jerga técnica sin explicar.
- Cero cifras inventadas. Si falta un número, se escribe `[FALTA DATO: qué se necesita y a quién se le pide]`.
- Cada paso del plano lleva dueño (puesto, no nombre de pila cuando el documento se comparte) y sistema donde vive.
- Los documentos que van al cliente no llevan líneas en blanco de más ni guiones largos, y los bloques pegables van dentro de cercas de código cuando la superficie necesita líneas en blanco.
- Un documento nunca se entrega sin haber corrido la compuerta de archivo del sistema con `--fase N`. Leer [07-auditoria.md](07-auditoria.md): formatos verificables, avisos de estilo y revisión humana que el script no sustituye.
## Encabezado obligatorio del expediente
Cada documento del expediente abre con un bloque de cuatro líneas: cliente, proceso, fase, y clase de evidencia dominante. Quien lo lea debe saber en diez segundos qué está viendo y cuánto vale.
## Dedupe
Antes de crear un documento o un caso en el expediente, buscar si ya existe. Si el tema ya vive en otro lado, se actualiza el existente preservando lo anterior con una nota de supersesión y el por qué. Dos verdades vigentes sobre lo mismo es el fracaso que esta regla existe para evitar.
## Frontera con el resto de tus herramientas
- Si trabajas junto a otras colecciones (oferta, precios, contenido), este sistema produce el contenido tecnico del diagnostico y no define oferta, precios ni catalogo.
- Los datos del cliente no salen del expediente y no entran a ningun archivo publicable.
