# Auditoría automática: alcance y límites
## Ejecución
Desde la carpeta de la skill: `python3 scripts/auditar-expediente.py /ruta/absoluta/del/expediente --fase N`.
Desde la raíz del repositorio: `python3 .agents/skills/plano-real/scripts/auditar-expediente.py /ruta/absoluta/del/expediente --fase N`.
La fase es obligatoria, de 0 a 5. Código 0 significa que pasaron los controles automáticos implementados; 1 indica fallas documentales; 2 indica uso incorrecto o ruta inexistente. Cero no certifica la veracidad ni sustituye la aprobación del cliente.
## Controles bloqueantes
- Archivos requeridos acumulados hasta la fase indicada y al menos una nota de entrevista desde fase 1.
- Enlaces locales a destinos existentes.
- Cada etiqueta de evidencia debe tener recibo en la misma línea o celda. Las fechas se escriben como AAAA-MM-DD y deben existir en el calendario.
- Dicho: cita entre comillas seguida de `(quién, puesto, AAAA-MM-DD, dónde)`.
- Observado: `caso ID caminado con PUESTO, el AAAA-MM-DD` (se permite texto descriptivo adicional).
- Aprobado: `[aprobado] DOCUMENTO versión ID aprobado por RESPONSABLE el AAAA-MM-DD (fuente: ruta/recibo)`. Exige formato, fecha válida y archivo dentro del expediente; no cuenta como evidencia.
- Firmado histórico: `DOCUMENTO revisado por RESPONSABLE el AAAA-MM-DD`. Se valida su formato, genera aviso de migración y no cuenta como evidencia ni como autorización vigente.
- Medido: `MÉTRICA con método MÉTODO: FÓRMULA = RESULTADO (fuente: ruta/archivo)`. La fuente es un archivo existente dentro del expediente, con ruta relativa al documento. Si el registro vive en un sistema externo, guardar su exportación o recibo local, no una URL desnuda.
- Los entregables operativos deben contener al menos una observación o medición; todos sus recibos marcados se validan.
- Cuando existe un bloque de diagrama generado, se verifica con el generador que no esté vencido.
## Avisos no bloqueantes
Estilo (líneas en blanco y guiones largos), marcadores FALTA DATO, ausencia global de etiquetas y brief posiblemente desactualizado por fecha de modificación. Un pendiente crítico puede impedir el cierre metodológico aunque el script termine en cero.
## Revisión humana obligatoria
El script no exige todavía la presencia de aprobaciones por fase ni valida que correspondan al contenido vigente; esa compuerta sigue siendo humana. El script no verifica la verdad de los recibos, no recalcula fórmulas, no detecta todas las cifras sin etiqueta, no comprueba exhaustivamente conteos de excepciones, cobertura de casos, firmas auténticas ni todas las compuertas metodológicas. La existencia de un archivo no prueba su suficiencia. Revisar estos puntos antes de cerrar; nunca anunciar que la auditoría los certifica.
## Compatibilidad y ejemplos
Los recibos abreviados que antes pasaban pueden fallar. Completar únicamente desde evidencia disponible; no inventar datos para pasar el auditor. `examples/expediente-ejemplo` es un ejemplo sintético de diagramación, no un expediente aprobado: conserva recibos incompletos que ahora se rechazan. Los tests contienen fixtures sintéticos de formato válido e inválido, sin datos de clientes.
## Mantenimiento
Toda regla bloqueante nueva necesita una prueba negativa que falle antes de implementarla y una comprobación positiva. Ejecutar desde la raíz: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`. No confundir pruebas de geometría del diagrama con pruebas de evidencia.
