# Migrar expedientes del contrato 0.6.1
Esta guía acompaña cambios aún sin publicar; no anuncia una release ni autoriza modificar un expediente real sin permiso. Los manifiestos conservan 0.6.1 hasta la publicación deliberada de una versión incompatible.
## Antes de migrar
1. Identificar cliente, alcance, fase real y ruta absoluta. Obtener permiso para modificar el expediente.
2. Hacer una copia íntegra en el espacio privado autorizado y comprobar que puede restaurarse. No sobreescribir recibos ni firmas históricas.
3. Auditar primero la copia. Registrar comando, código de salida y fallas; esta ejecución es un diagnóstico de compatibilidad, no aprobación.
## Cambios que requieren revisión
- Invocación: ahora `--fase N` es obligatorio (0 a 5). Desde la carpeta de la skill: `python3 scripts/auditar-expediente.py /ruta/absoluta/copia --fase N`. Las fases exigen archivos acumulados; no reducir N para ocultar faltantes.
- Evidencia: `dicho`, `observado` y `medido` requieren sus recibos completos. Completar únicamente desde fuentes disponibles; si falta un dato, registrarlo como pendiente, nunca inventarlo.
- Aprobación: conservar `[firmado]` como registro histórico. Para autorizar una versión vigente se necesita `[aprobado] DOCUMENTO versión ID aprobado por RESPONSABLE el AAAA-MM-DD (fuente: ruta/recibo)`. No convertir etiquetas automáticamente: verificar documento, versión, alcance y autoría.
- Fuentes: las rutas de recibos medidos y aprobados son relativas al documento y deben resolver a un archivo dentro del expediente. Una ruta absoluta se rechaza incluso si apunta dentro. Al convertirla, comprobar que el archivo y su contenido siguen siendo los mismos; no mover evidencia fuera del espacio autorizado.
- Encabezados: separar clase de evidencia y estado de aprobación. Si no hay evidencia, declarar su ausencia en lugar de inventar una clase.
- Alcance: marcar variantes excluidas como fuera de alcance. Los faltantes que sí afectan al tramo incluido siguen bloqueando su decisión.
## Verificación y reversión
1. Actualizar los documentos y el brief preservando trazabilidad hacia sus versiones anteriores.
2. Ejecutar la auditoría sobre el estado final de la copia; corregir fallas y repetir. Registrar el resultado sin modificar de nuevo la carpeta auditada.
3. Realizar revisión humana de fuentes, cálculos, excepciones, aprobaciones y compuertas. Código cero no certifica esos puntos.
4. Presentar el diff de la migración y sus pendientes al responsable antes de sustituir el expediente vigente. Conservar el original como respaldo; si no se aprueba, mantenerlo vigente y dejar la copia como propuesta.
La migración puede quedar incompleta por falta de evidencia. Eso no se resuelve relajando el auditor. El ejemplo de diagramación del repositorio no es un expediente aprobado y no debe rellenarse con recibos fabricados para hacerlo pasar.
