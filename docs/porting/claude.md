# Claude Code

Superficie: `.claude-plugin/plugin.json` y `.claude-plugin/marketplace.json`, con las skills en `.agents/skills/`.
Instalación:
```sh
claude plugin marketplace add ZarFer03/plano-real
claude plugin install plano-real@plano-real --scope user
```
Abre una sesión nueva después de instalar: los disparadores se registran al arrancar.
Invocación: automática por descripción, o `/plano-real:plano-real`.
Claude Desktop: abre Code, Local, elige la misma carpeta del diagnóstico y arranca una sesión nueva.
