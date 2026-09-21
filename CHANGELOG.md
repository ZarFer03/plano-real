# Changelog

Los cambios notables de `/plano-real` se registran aquí. Versionado semántico:

- **MAJOR:** un contrato del expediente o del flujo cambia de forma incompatible y necesita migración deliberada.
- **MINOR:** capacidad nueva o mejora de contrato compatible hacia atrás.
- **PATCH:** correcciones compatibles de comportamiento, documentación o empaquetado.

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
