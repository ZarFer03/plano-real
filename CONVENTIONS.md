# Convenciones de Plano Real
El contrato canónico vive dentro de la skill distribuible: [.agents/skills/plano-real/references/00-convenciones.md](.agents/skills/plano-real/references/00-convenciones.md). Leerlo antes de cualquier fase. Este archivo es una entrada, no otra copia del contrato.
Allí se definen evidencia y aprobación independientes, permisos, compuertas, avances delimitados, confidencialidad y deduplicación. Al actualizar un tema, modificar el contrato canónico en lugar de duplicarlo aquí.
## Auditoría
Desde la raíz del repositorio: `python3 .agents/skills/plano-real/scripts/auditar-expediente.py <ruta absoluta del expediente> --fase N` (N de 0 a 5).
Los controles automáticos y sus límites están en [.agents/skills/plano-real/references/07-auditoria.md](.agents/skills/plano-real/references/07-auditoria.md). Cero no certifica veracidad, aprobación auténtica ni cumplimiento completo de las compuertas.
## Compatibilidad
`[firmado]` se conserva únicamente como registro histórico, no como evidencia ni aprobación de una versión nueva. No convertir firmas históricas en aprobaciones nuevas sin recibo. `AGENTS.md` y el contrato canónico mantienen esta misma distinción.
