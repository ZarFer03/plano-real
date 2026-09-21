#!/usr/bin/env python3
"""Genera el diagrama del plano real desde la tabla de pasos.
El dibujo es derivado: nunca se edita a mano. La tabla manda.
Uso:
  python3 generar-diagrama.py 04_plano-real.md                    escribe el bloque Mermaid en la nota
  python3 generar-diagrama.py 04_plano-real.md --html salida.html tambien emite el entregable de una pagina
  python3 generar-diagrama.py 04_plano-real.md --check            sale 1 si el diagrama de la nota quedo viejo
"""
import html
import pathlib
import re
import sys

INICIO, FIN = "<!-- diagrama:inicio -->", "<!-- diagrama:fin -->"
SOLIDA = {"observado", "medido", "firmado"}
COLUMNAS = ["id", "paso", "quien", "sistema", "tipo", "excepcion", "ruta", "trabajo", "espera", "evidencia"]


def leer_pasos(texto):
    filas = []
    for linea in texto.split("\n"):
        l = linea.strip()
        if not l.startswith("|"):
            continue
        celdas = [c.strip() for c in l.strip("|").split("|")]
        if not celdas or set("".join(celdas)) <= set("-: "):
            continue
        if celdas[0].lower() == "id" or len(celdas) < 2:
            continue
        filas.append(dict(zip(COLUMNAS, celdas + [""] * (len(COLUMNAS) - len(celdas)))))
    return filas


def clase_evidencia(celda):
    c = (celda or "").lower()
    for k in ("observado", "medido", "firmado"):
        if k in c:
            return k
    if "dicho" in c:
        return "dicho"
    return "sin observar"


def partir(t, n=26):
    lineas, actual = [], ""
    for p in (t or "").split():
        if len(actual) + len(p) + 1 <= n:
            actual = (actual + " " + p).strip()
        else:
            lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas[:2]


def mermaid(pasos):
    out = ["```mermaid", "flowchart LR"]
    for p in pasos:
        etiqueta = p["paso"].replace('"', "'")
        if p["tipo"].lower().startswith("decid"):
            out.append('  n%s{{"%s"}}' % (p["id"], etiqueta))
        else:
            out.append('  n%s["%s"]' % (p["id"], etiqueta))
    for a, b in zip(pasos, pasos[1:]):
        extra = "|%s|" % b["sistema"] if b["sistema"] else ""
        out.append("  n%s -->%s n%s" % (a["id"], extra, b["id"]))
    rutas = [p for p in pasos if p["excepcion"] and p["excepcion"].lower() != "ninguna"]
    if rutas:
        out += ["  subgraph rutas de excepcion", "    direction TB"]
        for p in rutas:
            out.append('    e%s["%s: %s"]' % (p["id"], p["excepcion"], p["paso"][:40]))
            out.append("    n%s -.-> e%s" % (p["id"], p["id"]))
        out.append("  end")
    out.append("```")
    return "\n".join(out)


def etiqueta_corta(p):
    t = p["paso"]
    return t[:32] + ("..." if len(t) > 32 else "")


def svg(pasos, ancho=980, por_fila=4):
    AN, AL, HG, VG = 200, 56, 40, 90
    lineas = []
    for i, p in enumerate(pasos):
        fila, col = divmod(i, por_fila)
        y = 70 + fila * (AL + VG)
        x = 30 + col * (AN + HG)
        solida = clase_evidencia(p["evidencia"]) in SOLIDA
        borde = "#1A1A1A" if solida else "#9CA3AF"
        dash = "" if solida else ' stroke-dasharray="6 4"'
        relleno = "#FFFFFF" if solida else "#F3F4F6"
        if p["tipo"].lower().startswith("decid"):
            cx, cy = x + AN / 2, y + AL / 2
            pts = "%s,%s %s,%s %s,%s %s,%s" % (cx, y - 10, x + AN + 22, cy, cx, y + AL + 10, x - 22, cy)
            lineas.append('<polygon points="%s" fill="#FFFDF5" stroke="%s" stroke-width="2"%s/>' % (pts, borde, dash))
            lineas.append('<text x="%s" y="%s" class="nodo" text-anchor="middle">%s</text>' % (cx, cy - 2, html.escape(etiqueta_corta(p))))
            lineas.append('<text x="%s" y="%s" class="mini" text-anchor="middle">decide</text>' % (cx, cy + 14))
        else:
            lineas.append('<rect x="%s" y="%s" width="%s" height="%s" rx="8" fill="%s" stroke="%s" stroke-width="2"%s/>' % (x, y, AN, AL, relleno, borde, dash))
            for j, ln in enumerate(partir(p["paso"])):
                lineas.append('<text x="%s" y="%s" class="nodo">%s</text>' % (x + 14, y + 24 + j * 15, html.escape(ln)))
        if p["sistema"]:
            lineas.append('<text x="%s" y="%s" class="mini">%s</text>' % (x + 14, y + AL - 9, html.escape(p["sistema"][:30])))
        if p["espera"] and p["espera"] not in ("0", "0 min", "-"):
            lineas.append('<text x="%s" y="%s" class="mini espera" text-anchor="end">espera %s</text>' % (x + AN - 12, y + AL - 9, html.escape(p["espera"])))
        if p["excepcion"] and p["excepcion"].lower() != "ninguna":
            ey = y + AL + 8
            lineas.append('<rect x="%s" y="%s" width="%s" height="34" rx="6" fill="#FFF7ED" stroke="#C2410C" stroke-width="1.5" stroke-dasharray="5 4"/>' % (x, ey, AN))
            lineas.append('<text x="%s" y="%s" class="mini exc">%s</text>' % (x + 12, ey + 14, html.escape(p["excepcion"][:30])))
            lineas.append('<text x="%s" y="%s" class="mini">%s</text>' % (x + 12, ey + 27, html.escape((p["ruta"] or "sin ruta")[:34])))
            lineas.append('<path d="M%s,%s L%s,%s" stroke="#C2410C" stroke-width="1.5" stroke-dasharray="5 4"/>' % (x + AN / 2, y + AL, x + AN / 2, ey))
        if i + 1 < len(pasos):
            if col < por_fila - 1:
                x2 = 30 + (col + 1) * (AN + HG)
                lineas.append('<path d="M%s,%s L%s,%s" stroke="#1A1A1A" stroke-width="2" marker-end="url(#flecha)"/>' % (x + AN, y + AL / 2, x2 - 6, y + AL / 2))
            else:
                ny = 70 + (fila + 1) * (AL + VG)
                d = "M%s,%s L%s,%s L%s,%s L%s,%s L%s,%s" % (x + AN / 2, y + AL, x + AN / 2, ny - 34, 10, ny - 34, 10, ny + AL / 2, 24, ny + AL / 2)
                lineas.append('<path d="%s" fill="none" stroke="#1A1A1A" stroke-width="2" stroke-dasharray="8 5" marker-end="url(#flecha)"/>' % d)
    alto = ((len(pasos) - 1) // por_fila) * (AL + VG) + AL + 210
    cab = '<svg viewBox="0 0 %s %s" xmlns="http://www.w3.org/2000/svg" class="diagrama">' % (ancho, alto)
    defs = '<defs><marker id="flecha" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#1A1A1A"/></marker></defs>'
    leyenda = ('<rect x="600" y="14" width="16" height="12" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>'
               '<text x="624" y="25" class="mini">observado, medido o firmado</text>'
               '<rect x="600" y="34" width="16" height="12" fill="#F3F4F6" stroke="#9CA3AF" stroke-width="2" stroke-dasharray="6 4"/>'
               '<text x="624" y="45" class="mini">dicho o sin observar: no se toca</text>'
               '<rect x="600" y="54" width="16" height="12" fill="#FFF7ED" stroke="#C2410C" stroke-width="1.5" stroke-dasharray="5 4"/>'
               '<text x="624" y="65" class="mini">ruta de excepcion</text>')
    return "\n".join([cab, defs] + lineas + [leyenda, "</svg>"])


def horas(t):
    m = re.match(r"([\d.]+)\s*(min|h|horas?|d|dias?|días?)", (t or "").strip(), re.I)
    if not m:
        return 0.0
    v, u = float(m.group(1)), m.group(2).lower()
    if u.startswith("h"):
        return v
    if u.startswith("min"):
        return v / 60
    return v * 24


def contadores(pasos):
    decisiones = sum(1 for p in pasos if p["tipo"].lower().startswith("decid"))
    esperas = sum(horas(p["espera"]) for p in pasos)
    sinobs = sum(1 for p in pasos if clase_evidencia(p["evidencia"]) not in SOLIDA)
    return len(pasos), decisiones, esperas, sinobs


def entregable(pasos, meta):
    n, dec, esp, sinobs = contadores(pasos)
    exc = [p for p in pasos if p["excepcion"] and p["excepcion"].lower() != "ninguna"]
    filas = "\n".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (html.escape(p["paso"]), html.escape(p["excepcion"]), html.escape(p["ruta"] or "sin ruta"), html.escape(p["evidencia"][:60] or "sin evidencia"))
        for p in exc) or "<tr><td colspan='4'>Sin excepciones registradas.</td></tr>"
    css = (
        "@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Inter:wght@400;500;600&display=swap');\n"
        ":root{--accent:#2DD4BF;--text:#1A1A1A;--callout-bg:#F0FDF9;--callout-strong:#0F766E;--line:#1A1A1A;}\n"
        "*{margin:0;padding:0;box-sizing:border-box;}\n"
        "body{font-family:'Inter',system-ui,sans-serif;font-size:10pt;line-height:1.45;color:var(--text);background:#fff;width:216mm;min-height:279mm;margin:0 auto;padding:40pt 42pt;-webkit-print-color-adjust:exact;print-color-adjust:exact;}\n"
        "h1{font-family:'Montserrat',sans-serif;font-size:17pt;font-weight:700;letter-spacing:-0.2pt;}\n"
        "h2{font-family:'Montserrat',sans-serif;font-size:11pt;font-weight:600;margin:16pt 0 6pt;text-transform:uppercase;letter-spacing:0.6pt;}\n"
        ".sub{color:#4B5563;font-size:9pt;margin-top:3pt;}\n"
        ".rule{height:2pt;background:var(--accent);margin:10pt 0 14pt;}\n"
        ".hallazgo{background:var(--callout-bg);border-left:4pt solid var(--callout-strong);padding:9pt 11pt;margin:10pt 0 4pt;font-size:10.5pt;}\n"
        ".contadores{display:flex;gap:10pt;margin:12pt 0 4pt;}\n"
        ".card{flex:1;border:1.4pt solid var(--line);border-radius:6pt;padding:8pt 10pt;}\n"
        ".card b{font-family:'Montserrat',sans-serif;font-size:18pt;display:block;line-height:1.1;}\n"
        ".card span{font-size:8.5pt;color:#4B5563;}\n"
        ".diagrama{width:100%;height:auto;margin-top:6pt;}\n"
        ".nodo{font-family:'Inter',sans-serif;font-size:12.5px;font-weight:600;fill:#1A1A1A;}\n"
        ".mini{font-family:'Inter',sans-serif;font-size:10px;fill:#4B5563;}\n"
        ".espera{fill:#B45309;font-weight:600;}\n"
        ".exc{fill:#C2410C;font-weight:600;}\n"
        "table{width:100%;border-collapse:collapse;font-size:9pt;margin-top:4pt;}\n"
        "th,td{border:1pt solid var(--line);padding:4pt 6pt;text-align:left;vertical-align:top;}\n"
        "th{background:#F3F4F6;font-weight:600;}\n"
        ".pie{margin-top:14pt;border-top:1pt solid var(--line);padding-top:6pt;font-size:8pt;color:#4B5563;}\n"
        "@media print{body{width:100%;padding:32pt;} .no-print{display:none;}}\n"
        "@page{size:letter;margin:0;}\n")
    doc = ["<!DOCTYPE html>", '<html lang="es-MX"><head><meta charset="UTF-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
           "<title>Plano real: %s</title>" % html.escape(meta.get("proceso", "")),
           "<style>%s</style></head><body>" % css,
           "<h1>El plano real de la operación</h1>",
           '<div class="sub">%s · Proceso: %s · Fase: %s · Evidencia dominante: %s</div>' % (html.escape(meta.get("cliente", "")), html.escape(meta.get("proceso", "")), html.escape(meta.get("fase", "")), html.escape(meta.get("evidencia", ""))),
           '<div class="rule"></div>',
           '<div class="hallazgo">%s</div>' % html.escape(meta.get("hallazgo", "Sin hallazgo escrito todavia.")),
           '<div class="contadores">',
           '<div class="card"><b>%d</b><span>pasos</span></div>' % n,
           '<div class="card"><b>%d</b><span>puntos de decisión</span></div>' % dec,
           '<div class="card"><b>%g h</b><span>esperas acumuladas</span></div>' % esp,
           '<div class="card"><b>%d</b><span>pasos sin observar</span></div>' % sinobs,
           "</div>",
           "<h2>Cómo camina el trabajo</h2>",
           svg(pasos),
           "<h2>Rutas de excepción</h2>",
           "<table><tr><th>Paso</th><th>Excepción</th><th>Ruta</th><th>Evidencia</th></tr>%s</table>" % filas,
           '<div class="pie">Generado desde la tabla de pasos del expediente. El diagrama no se edita a mano: si la tabla cambia, se vuelve a generar. Los pasos en gris punteado están sin observar y no sostienen un rediseño todavía.</div>',
           "</body></html>"]
    return "\n".join(doc)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    nota = pathlib.Path(args[0])
    if not nota.exists():
        print("generar-diagrama: no existe la nota", nota)
        return 2
    texto = nota.read_text(encoding="utf-8")
    pasos = leer_pasos(texto)
    if not pasos:
        print("generar-diagrama: no encontre la tabla de pasos en", nota)
        return 1
    der = mermaid(pasos)
    if "--check" in args:
        actual = re.search(re.escape(INICIO) + r"(.*?)" + re.escape(FIN), texto, re.S)
        if not actual or actual.group(1).strip() != der.strip():
            print("generar-diagrama: el diagrama de la nota no coincide con la tabla de pasos")
            return 1
        print("generar-diagrama: el diagrama esta al dia")
        return 0
    bloque = INICIO + "\n" + der + "\n" + FIN
    if INICIO in texto and FIN in texto:
        texto = re.sub(re.escape(INICIO) + r".*?" + re.escape(FIN), lambda m: bloque, texto, flags=re.S)
    else:
        texto = texto.rstrip() + "\n## Diagrama del plano\nEl dibujo se genera desde la tabla de arriba y no se edita a mano.\n" + bloque + "\n"
    nota.write_text(texto, encoding="utf-8")
    n, dec, esp, sinobs = contadores(pasos)
    print("generar-diagrama: %d pasos | decisiones %d | esperas %g h | sin observar %d" % (n, dec, esp, sinobs))
    if "--html" in args:
        salida = pathlib.Path(args[args.index("--html") + 1])
        meta = {"cliente": "Cliente de ejemplo", "proceso": "Alta de una orden de servicio", "fase": "2, plano real", "evidencia": "observado",
                "hallazgo": "El caso espera mas de un dia sin que nadie lo trabaje, y la espera no esta en el area que todos culpan."}
        for etiqueta, clave in (("Cliente:", "cliente"), ("Proceso:", "proceso"), ("Fase:", "fase"), ("Evidencia dominante:", "evidencia"), ("Hallazgo:", "hallazgo")):
            m = re.search(re.escape(etiqueta) + r"\s*(.+)", texto)
            if m:
                meta[clave] = m.group(1).strip()
        salida.write_text(entregable(pasos, meta), encoding="utf-8")
        print("generar-diagrama: entregable escrito en", salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
