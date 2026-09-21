# Hermes

Dos rutas, y las dos son una línea.

Ruta rápida, por petición al agente: "instala las skills del repositorio ZarFer03/plano-real en mi perfil". El agente copia el árbol de `.agents/skills/plano-real/` a la carpeta de skills del perfil.

Ruta administrada, para que las actualizaciones se rastreen:

```sh
hermes skills install https://github.com/ZarFer03/plano-real
```

Esa ruta tarda más porque Hermes escanea cada skill por seguridad antes de aceptarla. A cambio, `hermes skills check` y `hermes skills update` mantienen la copia al día.

Nota de nombre: si tu instalación de Hermes ya tiene una skill llamada `plano-real`, renombra la carpeta al instalarla; los archivos no dependen del nombre.
