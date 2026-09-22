---
name: plano-real
description: Diagnostica y rediseña operaciones con evidencia.
---
# Plano Real: del caso real al cambio comprobado
Conduce un diagnóstico operativo: entender cómo se trabaja, medir, elegir un primer movimiento, rediseñar, probar y sostener. No sustituye la observación por una conversación ni convierte una firma en evidencia.
## Cuándo usar
- Entender cómo se ejecuta un proceso, dónde espera o de quién depende.
- Levantar casos, entrevistar a la operación o representar excepciones.
- Decidir qué simplificar antes de comprar software o automatizar.
- Retomar un diagnóstico y comprobar qué falta para avanzar.
- Verificar si un cambio mejoró la operación frente a su línea base.
No usar para contenido comercial, fijar precios, inventar el proceso ideal o presentar una opinión como diagnóstico aprobado.
## Mapa del ciclo
```text
Localizar expediente y decisión
              |
Arranque → Casos y entrevistas → Plano → Medición y prioridad
                                               |
                         Rediseño aprobado → Prueba → Custodia
              |
En cada intervención: verificar → archivar → entregar siguiente paso
```
Las rutas `references/` y `scripts/` se resuelven desde la carpeta que contiene este SKILL.md, no desde la carpeta del cliente. Antes de actuar, leer [el contrato](references/00-convenciones.md). Las fases mantienen sus compuertas; el avance independiente no autoriza cerrar el expediente completo.
## Paso 0: Localizar y evaluar el expediente
1. Resolver cliente, proceso y ruta absoluta. Buscar un expediente existente antes de crear otro. Si el destino es ambiguo, preguntar cuál; no escribir en una carpeta supuesta.
2. En una reanudación, leer `00_AGENT_BRIEF.md`, el alcance y los archivos de la fase solicitada. Comprobar lo que afirman contra sus fuentes, pendientes y aprobaciones; no confiar solo en el brief.
3. Clasificar la entrada: **nuevo** (preparar arranque), **retomable** (continuar desde evidencia existente), **incompleto** (recuperar el requisito faltante), o **destino incorrecto** (detener escritura y resolver ruta).
4. Comprobar permisos y accesos necesarios para el siguiente paso. Para ejecutar los scripts, comprobar Python 3.11 o superior. Para diagramar, revisar Node y ELK; si no están, declarar el acomodo interno y sus límites.
**Termina cuando:** cliente, proceso, destino y estado del expediente están identificados; están disponibles los insumos del siguiente paso o existe un bloqueo concreto. No entrevistar sin alcance y permisos.
## Paso 1: Precisar la decisión y el alcance
1. Expresar la decisión que el trabajo debe permitir en una frase: qué necesita decidir el cliente y sobre qué proceso.
2. Buscar objetivo, límites y aprobaciones existentes. No volver a preguntar lo ya confirmado; confirmar solo cambios, ambigüedades o decisiones nuevas.
3. Nombrar el artefacto a actualizar y el criterio observable de esta intervención. Si se piden trabajos distintos, separarlos y elegir el primero según dependencias.
4. Distinguir hechos por recuperar de decisiones por preguntar. No proponer cantidades, fechas, volúmenes ni causas sin recibo. En entrevista, una pregunta por turno, con hipótesis explícita que pueda corregirse.
**Termina cuando:** la decisión y el alcance constan en el expediente o fueron confirmados, y está definido qué resultado se producirá. Un dato faltante se registra, no se inventa.
## Paso 2: Ejecutar la fase correspondiente
Elegir por la petición **y los requisitos comprobados**, no por el nombre del archivo más avanzado. Leer la referencia completa antes de trabajar. En cada fase seguir objetivo, entrada, pasos, manejo de vacíos, archivos, cierre y entrega.
| Trabajo | Fase | Referencia |
|---|---|---|
| Acordar alcance, permisos, responsables y calendario | 0 | [Arranque y entrevistas](references/01-arranque-y-entrevistas.md) |
| Entrevistar y caminar casos reales | 1 | [Arranque y entrevistas](references/01-arranque-y-entrevistas.md) |
| Mapear pasos, rutas, excepciones y contadores | 2 | [Plano real](references/02-plano-real.md) |
| Medir y elegir un primer movimiento | 3 | [Medición y prioridad](references/03-medicion-y-prioridad.md) |
| Rediseñar, conseguir aprobación y probar | 4 | [Rediseño y prueba](references/04-rediseno-y-prueba.md) |
| Comprobar uso, sostener y aprender | 5 | [Custodia](references/05-sostener.md) |
Conservar las tres clases de evidencia y la aprobación independiente definidas en el contrato. No rediseñar lo no observado. Si falta un requisito, nombrarlo en una frase y pedir el primer dato faltante; solo continuar otro tramo si su independencia está documentada.
**Termina cuando:** los pasos de la intervención produjeron el artefacto con sus recibos, o un borrador delimitado identifica lo que falta, quién lo aporta y qué decisión bloquea. Un borrador no significa fase terminada.
## Paso 3: Verificar el resultado
1. Revisar la lista «Termina cuando» de la fase, no solo que exista el archivo.
2. Verificar que las fuentes sostienen cada afirmación, que los cálculos son reproducibles y que la aprobación corresponde a la versión. Son revisiones humanas que el script no sustituye.
3. Si cambian las tablas del plano, regenerar con [generar-diagrama.py](scripts/generar-diagrama.py); no editar el dibujo a mano. Revisar vigencia y legibilidad.
4. Leer [los controles y límites del auditor](references/07-auditoria.md). Desde la carpeta de la skill, ejecutar `python3 scripts/auditar-expediente.py "/ruta/absoluta/del/expediente" --fase N`, con la fase real de cierre. Corregir fallas y repetir; no bajar la fase para ocultarlas.
**Termina cuando:** para un cierre, las compuertas metodológicas están cumplidas y la auditoría sale en cero. Si no, informar «borrador» o «bloqueado» con el motivo exacto, sin anunciar aprobación o mejora.
## Paso 4: Archivar y entregar
1. Actualizar los documentos existentes preservando trazabilidad y registrando qué versión sustituyen. Guardar evidencia cruda en `fuentes/`, sin mezclarla con contenido publicable.
2. Actualizar `00_AGENT_BRIEF.md`: decisión, fase, archivos vigentes, evidencia, pendientes con responsable, bloqueos y siguiente acción. Si cambió después de auditar, repetir la auditoría sobre el estado final.
3. Entregar en el chat un resumen breve, no todo el expediente:
   - **Resultado:** qué quedó establecido y si es borrador, revisión o cierre.
   - **Sustento:** evidencia principal y su limitación.
   - **Archivo:** ubicación del artefacto actualizado.
   - **Pendiente:** qué falta, quién lo aporta y qué decisión bloquea.
   - **Siguiente movimiento:** una acción concreta, sin ejecutarla si requiere permiso.
**Termina cuando:** los archivos y el brief reflejan lo realmente hecho, el resultado de verificación está registrado y el usuario puede retomar el trabajo desde el siguiente movimiento.
## Límites y errores que evitar
- No prometer resultados, inventar cifras ni asumir permisos por tener acceso técnico.
- No cerrar con etiquetas vacías, aprobaciones de otra versión o un auditor verde como única prueba.
- No confundir evidencia con aprobación ni borrador con autorización para ejecutar.
- No volver a entrevistar desde cero si el expediente ya contiene la respuesta.
- No cambiar alcance, construir sin aprobación ni eliminar controles para cumplir una cuota.
- No sacar datos del cliente del expediente ni usarlos públicamente sin permiso escrito.
- No sustituir una visita o una prueba real por una simulación no declarada.
## Mapa de archivos del expediente
| Archivo | Función |
|---|---|
| `00_AGENT_BRIEF.md` | Estado y continuidad para quien retome |
| `01_alcance.md` | Proceso, entregables, límites, precio y fechas confirmados |
| `02_quien-es-quien.md` | Quién decide, ejecuta, autoriza y sostiene |
| `03_entrevistas/` | Notas con casos, citas, recibos y pendientes |
| `04_plano-real.md` | Nodos, rutas, excepciones, contadores y diagrama |
| `05_linea-base.md` | Datos, método, ventana, fuentes y cálculos |
| `06_prioridad.md` | Criterio y primer movimiento |
| `07_rediseno.md` | Nuevo proceso y aprobación de versión |
| `08_prueba.md` | Criterio previo, ejecución, comparación y reversión |
| `09_custodia.md` | Uso, responsables, incidentes y siguiente ciclo |
| `fuentes/` | Registros crudos y recibos |
