# Changelog

Los cambios notables de `/plano-real` se registran aquí. Versionado semántico:

- **MAJOR:** un contrato del expediente o del flujo cambia de forma incompatible y necesita migración deliberada.
- **MINOR:** capacidad nueva o mejora de contrato compatible hacia atrás.
- **PATCH:** correcciones compatibles de comportamiento, documentación o empaquetado.

## 0.2.1

Margenes de texto conservadores, para que ninguna etiqueta toque el borde de su forma.

### Impacto

- El ancho de linea de cada simbolo se recorta segun la forma: el paralelogramo y el trapecio pierden ancho por el sesgo, y el rombo solo tiene el centro util.
- La etiqueta del carril se recorta a 22 caracteres para que no invada el margen izquierdo.
- Verificacion geometrica agregada: se revisa que ningun texto se salga del lienzo ni de su forma.

### Compatibilidad

- Compatible. Solo cambia el corte de linea de las etiquetas.

### Actualizacion

- Volver a instalar y regenerar el diagrama.

### Migracion

- Ninguna.

### Entrega

- Ejemplo regenerado: 58 textos, ninguno fuera de su caja, cero traslapes.

## 0.2.0

El diagrama pasa a los simbolos de ISO 5807 y se dibuja en vertical, como se lee un flujograma.

### Impacto

- Simbolos correctos, no cajas genericas: terminador para inicio y fin, rectangulo para actividad, rombo para decision, documento con el borde ondulado para registros, paralelogramo para datos, cilindro para sistemas y forma de D para la demora.
- El juego del cursograma OTIDA queda disponible con `--set cursograma`: circulo para operacion, cuadrado para inspeccion, flecha ancha para transporte.
- La espera deja de ser una columna y se vuelve un simbolo: el generador inserta una demora entre dos pasos cada vez que la tabla declara espera, con el tiempo adentro. Diez esperas y 116 horas se ven de un golpe.
- Acomodo vertical con carril de puestos a la izquierda y rutas de excepcion a la derecha. Cada cambio de dueno se ve en el carril.
- El generador se autoinspecciona: si el acomodo produce formas encimadas, lo reporta y no entrega. Estado actual del ejemplo: cero traslapes.
- Nueva referencia `references/06-simbolos-y-normas.md` con que exige ISO 9001, el juego completo de ISO 5807, el del cursograma y las reglas de flujo.

### Compatibilidad

- La tabla de pasos gana una columna opcional `forma`. Sin ella, el generador deduce la forma del tipo de paso y del juego de simbolos, asi que las tablas viejas siguen funcionando.
- El bloque Mermaid de las notas anteriores cambia; volver a generar lo actualiza.

### Actualizacion

- Volver a instalar y regenerar el diagrama de las notas existentes.

### Migracion

- Ninguna sobre datos de cliente.

### Entrega

- Ejemplo regenerado en `examples/` con las formas declaradas, y verificacion de traslapes en cero.

## 0.1.1

El diagrama del plano deja de ser un dibujo y se vuelve un derivado de la tabla de pasos.

### Impacto

- Nuevo script `generar-diagrama.py`: lee la tabla de pasos del expediente y escribe el diagrama Mermaid dentro de la nota, además del entregable de una página en HTML con la marca, listo para imprimir.
- El dibujo lleva la verdad a la vista: los pasos observados, medidos o firmados van en línea sólida, y los que solo se dijeron, en gris punteado. Los romanos de la excepción van como ruta aparte.
- Contadores automáticos: pasos, puntos de decisión y esperas acumuladas, sumadas desde la propia tabla.
- La auditoría del expediente gana un chequeo: si la tabla de pasos cambió y el diagrama no se regeneró, marca `diagrama_vencido` y el entregable no se puede cerrar.
- Ejemplo completo en `examples/`, con expediente y entregable renderizado.

### Compatibilidad

- Compatible hacia atrás. El script de auditoría sigue funcionando igual y el chequeo nuevo solo aplica cuando la nota tiene el bloque de diagrama marcado.

### Actualización

- Volver a instalar el plugin o el marketplace según la ruta que uses. No hay nada que migrar.

### Migración

- Ninguna.

### Entrega

- Probado de punta a punta: generar, verificar que está al día, editar solo la tabla y comprobar que tanto `generar-diagrama.py --check` como la auditoría lo detectan, y regenerar.

## 0.1.0

Primera versión pública del método, empaquetado como skill instalable.

### Impacto

- Seis fases con compuerta: arranque, entrevistas, plano real, medición y prioridad, rediseño y prueba, sostenimiento.
- Cuatro clases de evidencia con lo que cada una permite y prohíbe, y la regla de que no se rediseña lo que no se observó.
- Barrido de excepciones en siete familias, con sus cinco datos y sus tres preguntas obligatorias.
- Auditores de expediente ejecutables, que condicionan el cierre de cada entregable.

### Compatibilidad

- Nuevo. No hay versiones anteriores ni migración.
- Instalable en Claude Code vía plugin, en Codex/ChatGPT vía marketplace de Codex o por petición directa en un chat, y en Hermes por petición al agente.

### Actualización

- Nada que hacer. Primera versión.

### Migración

- Ninguna.

### Entrega

- El árbol canónico es `.agents/skills/plano-real/`. Los manifiestos de instalación de cada arnés viven en `.claude-plugin/`, `.codex-plugin/` y `.agents/plugins/`.
- Probado el script de auditoría contra tres expedientes de prueba: uno limpio en cero, uno roto con seis fallas, y uno con un `dicho` sin recibo.
