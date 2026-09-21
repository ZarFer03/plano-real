# Plano Real, charter para agentes

Este repositorio contiene un método de diagnóstico de operaciones empaquetado como skills. Si eres un agente que entra aquí, esto es lo que necesitas saber antes de escribir una línea.

## Qué es

Un sistema de trabajo, no una librería de prompts. Conduce el levantamiento, la medición y el rediseño de la operación real de una empresa, con disciplina de evidencia.

## El árbol canónico

`.agents/skills/plano-real/` es la única fuente de verdad del método:

- `SKILL.md` el router: las leyes, las compuertas entre fases y la tabla de qué archivo leer para cada trabajo.
- `references/` las seis fases, con sus pasos, sus entregables y su compuerta de cierre.
- `scripts/auditar-expediente.py` la compuerta de archivo.

`AGENTS.md` y `CLAUDE.md` son la entrada. `CONVENTIONS.md` son los contratos compartidos. Las carpetas `.claude-plugin/`, `.codex-plugin/` y `.agents/plugins/` son manifiestos de instalación, no documentación.

## Cómo se trabaja

1. Lee `CONVENTIONS.md`.
2. Lee `SKILL.md` y elige la fase con su tabla de router.
3. Lee el archivo de `references/` de esa fase antes de trabajar. Escribir de memoria produce artefactos genéricos.
4. Antes de cerrar cualquier artefacto, corre el script de auditoría y déjalo en cero.

## Las cinco leyes, en corto

1. Nada entra como hecho sin recibo: `dicho`, `observado`, `medido` o `firmado`.
2. No se rediseña lo que no se observó.
3. Hechos se buscan, decisiones se preguntan.
4. Una pregunta por turno, con hipótesis de trabajo.
5. Nunca afirmar antes de preguntar.

## Lo que no se negocia

- Ninguna cifra sin fuente, ni siquiera como ejemplo.
- Ningún paso del plano sin haber caminado el caso.
- Ninguna excepción sin conteo que sostenga un rediseño.
- Ningún entregable que no pase la compuerta de archivo.
- Ningún dato del cliente fuera del expediente.

Si falta algo para poder completar el trabajo, se dice en una frase y se hace la primera pregunta que falta. No se rellena.
