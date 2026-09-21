# /plano-real

Un método, no un cuestionario. Cómo levantar la operación real de una empresa, medirla y rediseñarla.

Una operación no se arregla comprando otra herramienta. Se arregla entendiéndola. Este sistema conduce el trabajo que hace falta para eso, dentro de Claude, Codex/ChatGPT o Hermes, y se niega a producir un documento sin sustento.

## Qué lo hace distinto

- **No salta fases.** El orden es arranque, entrevistas, plano, medición, prioridad, rediseño, prueba y sostenimiento. Si falta la fase anterior, no produce el artefacto: hace la primera pregunta que falta. Un plano sin casos caminados es una invención.
- **Nada entra como hecho sin recibo.** Toda afirmación sobre la operación es `dicho`, `observado`, `medido` o `firmado`, y cada clase tiene lo que permite y lo que prohíbe. De ahí sale la ley que sostiene todo: **no se rediseña lo que no se observó**. Un paso que nadie vio ejecutar no se borra ni se automatiza.
- **Las excepciones son el trabajo real.** Siete familias (dato faltante, autorización, tipo de caso, tiempo, capacidad, sistema y decisión humana), cada una con su disparador, quién la atiende, a dónde desvía, cuántas veces pasa y qué cuesta. Sin conteo, una excepción no puede sostener un rediseño.
- **Todo queda en tu expediente.** Archivos de markdown en tu propia carpeta, en un formato que puedes leer, versionar y llevarte. Nada vive solo dentro de un chat.
- **El cierre está condicionado.** Un script audita el expediente antes de dar cualquier entregable por terminado: archivos de la fase, enlaces rotos, evidencia faltante, excepciones sin conteo, números sin fuente. Si no sale en cero, no está terminado.

## Instalar

### Claude Code

```sh
claude plugin marketplace add ZarFer03/plano-real
mkdir -p mi-diagnostico && cd mi-diagnostico
claude plugin install plano-real@plano-real --scope user
claude
```

La última línea abre una sesión nueva, y eso importa: los disparadores de las skills se registran al arrancar. En esa sesión escribes `/plano-real:plano-real` o simplemente pides el trabajo en lenguaje natural.

### Codex y ChatGPT (Codex CLI)

```sh
codex plugin marketplace add ZarFer03/plano-real
```

Después abre `/plugins`, instala y arranca una sesión nueva. Se invoca sola por descripción o con `$plano-real`.

### ChatGPT sin plugins

Un chat nuevo no puede instalar plugins, así que se le pide directo. Pega esto:

> Descarga el repositorio https://github.com/ZarFer03/plano-real y usa los archivos de `.agents/skills/plano-real/` como tus instrucciones de este proyecto. Empieza leyendo `SKILL.md` y abre las referencias de `references/` cuando la tarea lo pida.

### Hermes

Pídeselo al agente, nombrando el repositorio y dónde quieres que queden los archivos:

> Instala las skills del repositorio `ZarFer03/plano-real` en mi perfil.

## Cómo se usa

El sistema elige la fase según lo que pidas y lo que el expediente ya tenga. Cada fase vive en su archivo dentro de `references/`, y se lee antes de trabajar.

| Lo que pides | Fase | Archivo |
|---|---|---|
| Arrancar con un cliente: alcance, quién es quién, accesos, calendario | 0 | `01-arranque-y-entrevistas.md` |
| Entrevistar a la operación y entender el trabajo real | 1 | `01-arranque-y-entrevistas.md` |
| Levantar el plano con sus pasos y sus excepciones | 2 | `02-plano-real.md` |
| Medir, línea base, contar pasos, esperas y horas manuales | 3 | `03-medicion-y-prioridad.md` |
| Decidir qué construir primero | 3 | `03-medicion-y-prioridad.md` |
| Rediseñar: borrar, simplificar, conectar, automatizar | 4 | `04-rediseno-y-prueba.md` |
| Probar contra la línea base | 4 | `04-rediseno-y-prueba.md` |
| Sostener, adopción y comparación | 5 | `05-sostener.md` |
| Auditar el expediente antes de entregar | todas | `scripts/auditar-expediente.py` |

## Las cinco leyes

1. Nada entra como hecho sin recibo.
2. No se rediseña lo que no se observó.
3. Hechos se buscan, decisiones se preguntan.
4. Una pregunta por turno, y cada pregunta con una hipótesis.
5. Nunca afirmar antes de preguntar.

Los contratos completos, con las clases de evidencia y las compuertas entre fases, están en [CONVENTIONS.md](CONVENTIONS.md).

## El expediente

Un expediente por cliente, y esta es su forma:

```
00_AGENT_BRIEF.md   el brief para cualquier agente: confirmado, pendiente y cómo razonar
01_alcance.md       proceso elegido, fases, entregables, fechas
02_quien-es-quien.md puestos, quién decide, quién ejecuta, quién autoriza
03_entrevistas/     una nota por entrevista, con su recibo
04_plano-real.md    el flujo, sus pasos, sus excepciones y su diagrama
05_linea-base.md    lo contado, con su método y su fórmula
06_prioridad.md     el orden de lo que conviene construir primero
07_rediseno.md      el proceso nuevo, con sus excepciones diseñadas
08_prueba.md        qué se probó, con qué casos y contra qué número
09_custodia.md      adopción, comparación y siguiente ciclo
fuentes/            los registros crudos que dio el cliente
```

## Qué no hace

No decide precios ni alcance comercial. No escribe material publicable: los datos del cliente no salen del expediente. No sustituye la visita presencial ni la junta. No inventa reglas de la operación: si falta un dato, escribe `[FALTA DATO: qué se necesita y a quién se le pide]`.

## Estructura del repositorio

- `.agents/skills/plano-real/` el árbol canónico: `SKILL.md`, `references/` y `scripts/`.
- `.claude-plugin/`, `.codex-plugin/` y `.agents/plugins/` los manifiestos de instalación de cada arnés.
- `docs/porting/` las notas de instalación por plataforma.
- `CONVENTIONS.md` los contratos que comparten todas las fases. `AGENTS.md` el charter para cualquier agente que entre al repositorio.

## Licencia

MIT. Úsalo, modifícalo y móntalo en tu operación. Autor: Genaro Acosta.
