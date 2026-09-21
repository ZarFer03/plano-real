# Codex CLI y ChatGPT

Superficie: `.agents/skills` más `.codex-plugin/plugin.json` y `.agents/plugins/marketplace.json`. Codex también lee el marketplace de Claude como formato heredado.
Instalación en la CLI:
```sh
codex plugin marketplace add ZarFer03/plano-real
```
Después abre `/plugins`, instala y arranca una sesión nueva.
Invocación: automática por descripción, o `$plano-real`. Los metadatos de cada skill viven en `agents/openai.yaml`, nunca en el frontmatter de `SKILL.md`.
ChatGPT sin plugins: no hay instalación posible, así que se le pide al chat que descargue el repositorio y use `.agents/skills/plano-real/` como instrucciones del proyecto. El texto exacto está en el README.
Nota: el catálogo recorta las descripciones largas, así que el disparador va siempre al principio de la descripción.
