#!/usr/bin/env python3
"""Genera el diagrama del plano real desde la tabla de pasos.
Simbolos ISO 5807 por defecto, o del cursograma OTIDA con --set cursograma.
El dibujo es derivado: nunca se edita a mano. La tabla manda.
Pagina el diagrama solo, con conectores, para que cada hoja se lea sin amontonarse.

Uso:
  python3 generar-diagrama.py 04_plano-real.md                      escribe el bloque Mermaid en la nota
  python3 generar-diagrama.py 04_plano-real.md --html salida.html   emite ademas el entregable
  python3 generar-diagrama.py 04_plano-real.md --check              sale 1 si el diagrama de la nota quedo viejo
  python3 generar-diagrama.py 04_plano-real.md --diagnostico        reporta traslapes, huecos y resumen
  --set iso5807 | cursograma        juego de simbolos
  --por-pagina N                    elementos por hoja (por defecto 7)
"""
import html
import pathlib
import re
import sys

INICIO, FIN = "<!-- diagrama:inicio -->", "<!-- diagrama:fin -->"
SOLIDA = {"observado", "medido", "firmado"}
LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# forma: (alto, caracteres por linea, aire extra abajo)
FORMAS = {
    "inicio": (46, 30, 0), "fin": (46, 30, 0),
    "actividad": (64, 38, 0), "documento": (72, 38, 0), "datos": (64, 36, 0),
    "entrada-manual": (68, 34, 0), "demora": (46, 20, 0), "base-de-datos": (74, 34, 0),
    "almacenamiento": (64, 32, 0), "preparacion": (64, 34, 0), "subproceso": (64, 36, 0),
    "conector": (56, 4, 0), "decision": (104, 24, 22), "operacion": (92, 20, 0),
    "inspeccion": (92, 20, 0), "transporte": (64, 30, 0),
}
ANCHO_NODO, ANCHO_DEC, ANCHO_ESPERA = 340, 250, 150
X_CARRIL, X_MAIN, X_EXC = 180.0, 350.0, 770.0
ANCHO_EXC, ANCHO_LIENZO = 200.0, 1000.0
HUECO, HUECO_ESPERA = 26, 22


def leer_tabla(texto):
    encabezado, filas = None, []
    for linea in texto.split("\n"):
        l = linea.strip()
        if not l.startswith("|"):
            continue
        celdas = [c.strip() for c in l.strip("|").split("|")]
        if not celdas or set("".join(celdas)) <= set("-: "):
            continue
        if encabezado is None:
            encabezado = [c.lower() for c in celdas]
            continue
        fila = {k: "" for k in encabezado}
        for i, c in enumerate(celdas):
            if i < len(encabezado):
                fila[encabezado[i]] = c
        if fila.get("paso"):
            filas.append(fila)
    return filas


def clase_evidencia(celda):
    c = (celda or "").lower()
    for k in ("observado", "medido", "firmado"):
        if k in c:
            return k
    return "dicho" if "dicho" in c else "sin observar"


def resolver_forma(p, juego):
    f = (p.get("forma") or "").strip().lower()
    if f in FORMAS:
        return f
    if (p.get("tipo") or "").lower().startswith("decid"):
        return "decision"
    return "operacion" if juego == "cursograma" else "actividad"


def wrap(t, n):
    lineas, actual = [], ""
    for palabra in (t or "").split():
        if len(actual) + len(palabra) + 1 <= n:
            actual = (actual + " " + palabra).strip()
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas or [""]


def minutos(t):
    m = re.match(r"([\d.]+)\s*(min|h|horas?|d|dias?|días?)", (t or "").strip(), re.I)
    if not m:
        return 0.0
    v, u = float(m.group(1)), m.group(2).lower()
    return v * 60 if u.startswith("h") else (v if u.startswith("min") else v * 1440)


def bonito(m):
    if m >= 1440 and m % 1440 == 0:
        return "%g d" % (m / 1440)
    return ("%g h" % (m / 60)) if m >= 60 else ("%g min" % m)


def forma_svg(f, x, y, w, h, solida):
    borde = "#1A1A1A" if solida else "#9CA3AF"
    dash = "" if solida else ' stroke-dasharray="6 4"'
    relleno = "#FFFFFF" if solida else "#F3F4F6"
    a = 'fill="%s" stroke="%s" stroke-width="2"%s' % (relleno, borde, dash)
    cx, cy = x + w / 2, y + h / 2
    if f in ("inicio", "fin"):
        return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" %s/>' % (x, y, w, h, h / 2, a)
    if f in ("actividad", "subproceso"):
        s = '<rect x="%s" y="%s" width="%s" height="%s" rx="6" %s/>' % (x, y, w, h, a)
        if f == "subproceso":
            s += '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="2"/><line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="2"/>' % (x + 18, y, x + 18, y + h, borde, x + w - 18, y, x + w - 18, y + h, borde)
        return s
    if f == "preparacion":
        return '<polygon points="%s,%s %s,%s %s,%s %s,%s %s,%s %s,%s" %s/>' % (x + 20, y, x + w - 20, y, x + w, cy, x + w - 20, y + h, x + 20, y + h, x, cy, a)
    if f == "decision":
        return '<polygon points="%s,%s %s,%s %s,%s %s,%s" %s/>' % (cx, y, x + w, cy, cx, y + h, x, cy, a)
    if f == "datos":
        return '<polygon points="%s,%s %s,%s %s,%s %s,%s" %s/>' % (x + 22, y, x + w, y, x + w - 22, y + h, x, y + h, a)
    if f == "entrada-manual":
        return '<polygon points="%s,%s %s,%s %s,%s %s,%s" %s/>' % (x + 26, y, x + w, y + 16, x + w, y + h, x, y + h, a)
    if f == "documento":
        d = "M%s,%s H%s V%s C%s,%s %s,%s %s,%s H%s Z" % (x, y, x + w, y + h - 14, x + w * .75, y + h + 8, x + w * .25, y + h - 26, x, y + h - 6, x)
        return '<path d="%s" %s/>' % (d, a)
    if f == "almacenamiento":
        return '<polygon points="%s,%s %s,%s %s,%s" %s/>' % (x, y, x + w, y, cx, y + h, a)
    if f == "demora":
        r = h / 2
        return '<path d="M%s,%s H%s A%s,%s 0 0 1 %s,%s H%s Z" %s/>' % (x, y, x + w - r, r, r, x + w - r, y + h, x, a)
    if f == "base-de-datos":
        ry = 9
        return '<path d="M%s,%s V%s A%s,%s 0 0 0 %s,%s V%s A%s,%s 0 0 0 %s,%s Z" %s/>' % (x, y + ry, y + h - ry, w / 2, ry, x + w, y + h - ry, y + ry, w / 2, ry, x, y + ry, a)
    if f == "transporte":
        return '<polygon points="%s,%s %s,%s %s,%s %s,%s %s,%s %s,%s" %s/>' % (x, y, x + w - 30, y, x + w - 30, y - 8, x + w, cy, x + w - 30, y + h + 8, x + w - 30, y + h, a)
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" %s/>' % (cx, cy, w / 2, h / 2, a)


def texto_svg(lineas, x, y, clase="nodo", centro=None):
    anclaje = ' text-anchor="middle"' if centro else ""
    px = centro if centro else x
    return ['<text x="%s" y="%s" class="%s"%s>%s</text>' % (px, y + j * 15, clase, anclaje, html.escape(ln)) for j, ln in enumerate(lineas)]


def elementos(pasos, juego):
    lista = [{"tipo": "inicio", "p": {"paso": "Inicio del proceso"}}]
    for p in pasos:
        lista.append({"tipo": "paso", "p": p})
    lista.append({"tipo": "fin", "p": {"paso": "Fin del caso"}})
    return lista


def dibujar_pagina(els, meta, juego, primera, ultima, letra_antes, letra_siguiente):
    bboxes, svg, carriles = [], [], []
    y = 46.0
    if not primera:
        svg.append(forma_svg("conector", X_MAIN + (ANCHO_NODO - 56) / 2, y, 56, 56, True))
        svg += texto_svg([letra_antes], 0, y + 36, "nodo", centro=X_MAIN + ANCHO_NODO / 2)
        bboxes.append((X_MAIN + (ANCHO_NODO - 56) / 2, y, 56, 56, "conector"))
        carriles.append((y, y + 56, "viene de la hoja anterior"))
        y += 56 + HUECO
    for el in els:
        p, tipo = el["p"], el["tipo"]
        f = "inicio" if tipo == "inicio" else ("fin" if tipo == "fin" else resolver_forma(p, juego))
        h, chars, extra = FORMAS.get(f, FORMAS["actividad"])
        espera = minutos(p.get("espera", "")) if tipo == "paso" else 0
        exc = (p.get("excepcion") or "").strip()
        tiene_exc = tipo == "paso" and exc and exc.lower() != "ninguna"
        y_banda = y
        if espera > 0:
            hd = FORMAS["demora"][0]
            xd = X_MAIN + (ANCHO_NODO - ANCHO_ESPERA) / 2
            svg.append(forma_svg("demora", xd, y, ANCHO_ESPERA, hd, True))
            svg += texto_svg(["espera %s" % bonito(espera)], 0, y + hd / 2 + 5, "demora", centro=xd + ANCHO_ESPERA / 2)
            bboxes.append((xd, y, ANCHO_ESPERA, hd, "demora"))
            y += hd + HUECO_ESPERA
        solida = clase_evidencia(p.get("evidencia", "")) in SOLIDA or tipo in ("inicio", "fin")
        if f == "decision":
            an = ANCHO_DEC
        elif f == "demora":
            an = ANCHO_ESPERA
        elif f in ("operacion", "inspeccion", "conector"):
            an = 150.0
        else:
            an = ANCHO_NODO
        x = X_MAIN + (ANCHO_NODO - an) / 2
        svg.append(forma_svg(f, x, y, an, h, solida))
        rotulo = wrap(p.get("paso", ""), chars)
        if f == "decision":
            svg += texto_svg(rotulo, 0, y + h / 2 - 13 - 6 * (len(rotulo) - 1) + 5, "nodo", centro=x + an / 2)
            if p.get("sistema"):
                svg += texto_svg([p["sistema"][:30]], 0, y + h / 2 + 17, "mini", centro=x + an / 2)
            if p.get("condicion"):
                svg += texto_svg([wrap(p["condicion"], 26)[0]], 0, y + h + 17, "rama", centro=x + an / 2)
        elif f == "conector":
            svg += texto_svg(rotulo, 0, y + h / 2 + 5, "nodo", centro=x + an / 2)
        else:
            svg += texto_svg(rotulo, x + 16, y + 26, "nodo")
            if p.get("sistema"):
                svg += texto_svg([p["sistema"][:32]], x + 16, y + h - 14, "mini")
        bboxes.append((x, y, an, h, f))
        y += h + extra
        if tiene_exc:
            l_exc = wrap(exc, 22) + wrap(p.get("ruta") or "sin ruta declarada", 25)[:2]
            if p.get("regreso"):
                l_exc.append("vuelve al paso %s" % p["regreso"])
            alto_exc = 16 + len(l_exc) * 13 + 8
            y_exc = max(y_banda, y - extra - alto_exc + 4)
            svg.append('<rect x="%s" y="%s" width="%s" height="%s" rx="4" fill="#FFF7ED" stroke="#C2410C" stroke-width="1.5" stroke-dasharray="5 4"/>' % (X_EXC, y_exc, ANCHO_EXC, alto_exc))
            svg += texto_svg([l_exc[0]], X_EXC + 12, y_exc + 18, "exc")
            svg += texto_svg(l_exc[1:], X_EXC + 12, y_exc + 33, "mini")
            svg.append('<path d="M%s,%s L%s,%s" stroke="#C2410C" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#flechaNaranja)"/>' % (x + an + 10, y - extra - h / 2, X_EXC - 8, y_exc + alto_exc / 2))
            if p.get("condicion"):
                medio = (x + an + 10 + X_EXC - 8) / 2
                svg += texto_svg([wrap(p["condicion"], 20)[0]], 0, y - extra - h / 2 - 7, "rama", centro=medio)
            bboxes.append((X_EXC, y_exc, ANCHO_EXC, alto_exc, "excepcion"))
            y = max(y, y_exc + alto_exc) + HUECO
        else:
            y += HUECO
        carriles.append((y_banda, y, p.get("quien") or ""))
    if not ultima:
        svg.append(forma_svg("conector", X_MAIN + (ANCHO_NODO - 56) / 2, y, 56, 56, True))
        svg += texto_svg([letra_siguiente], 0, y + 36, "nodo", centro=X_MAIN + ANCHO_NODO / 2)
        bboxes.append((X_MAIN + (ANCHO_NODO - 56) / 2, y, 56, 56, "conector"))
        carriles.append((y, y + 56, "sigue en la hoja siguiente"))
        y += 56
    alto = y + 30
    cab = '<svg viewBox="0 0 %g %g" xmlns="http://www.w3.org/2000/svg" class="diagrama">' % (ANCHO_LIENZO, alto)
    defs = ('<defs><marker id="flecha" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#1A1A1A"/></marker>'
            '<marker id="flechaNaranja" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#C2410C"/></marker></defs>')
    out = [cab, defs, '<line x1="%g" y1="6" x2="%g" y2="%g" stroke="#D1D5DB" stroke-width="1.5"/>' % (X_CARRIL, X_CARRIL, alto - 6)]
    anterior = None
    for y0, y1, quien in carriles:
        if quien and quien != anterior:
            out.append('<line x1="0" y1="%s" x2="%g" y2="%s" stroke="#D1D5DB" stroke-width="1.5"/>' % (y0, X_CARRIL, y0))
            out.append('<text x="%s" y="%s" class="carril">%s</text>' % (X_CARRIL - 12, (y0 + y1) / 2 + 4, html.escape(quien[:22])))
            anterior = quien
    centros = [(b[0] + b[2] / 2, b[1], b[3]) for b in bboxes if b[4] != "excepcion"]
    for (cx1, y1, h1), (cx2, y2, h2) in zip(centros, centros[1:]):
        if y2 > y1 + h1:
            out.append('<path d="M%s,%s L%s,%s" stroke="#1A1A1A" stroke-width="2" marker-end="url(#flecha)"/>' % (cx1, y1 + h1, cx2, y2))
    return "\n".join(out + svg + ["</svg>"]), bboxes, alto


def colisiones(bboxes):
    fallas = []
    for i in range(len(bboxes)):
        for j in range(i + 1, len(bboxes)):
            ax, ay, aw, ah, an = bboxes[i]
            bx, by, bw, bh, bn = bboxes[j]
            if ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah:
                fallas.append((an, bn, round(ay), round(by)))
    return fallas


def paginas(pasos, juego, por_pagina):
    els = elementos(pasos, juego)
    if por_pagina <= 0 or len(els) <= por_pagina + 1:
        return [els]
    salida = []
    i = 0
    while i < len(els):
        salida.append(els[i:i + por_pagina])
        i += por_pagina
    if len(salida) > 1 and len(salida[-1]) < 3:
        salida[-2] += salida.pop()
    return salida


def dibujar(pasos, meta, juego="iso5807", por_pagina=7):
    pags = paginas(pasos, juego, por_pagina)
    svgs, cajas, altos = [], [], []
    for i, els in enumerate(pags):
        letra_antes = LETRAS[i - 1] if i > 0 else ""
        letra_sig = LETRAS[i] if i < len(pags) - 1 else ""
        s, b, a = dibujar_pagina(els, meta, juego, i == 0, i == len(pags) - 1, letra_antes, letra_sig)
        svgs.append(s)
        cajas.append(b)
        altos.append(a)
    return svgs, cajas, altos


def mermaid(pasos, juego):
    mapa = {"inicio": ("([", "])"), "fin": ("([", "])"), "actividad": ("[", "]"), "subproceso": ("[[", "]]"),
            "preparacion": ("{{", "}}"), "decision": ("{", "}"), "datos": ("[/", "/]"), "documento": ("[/", "\\]"),
            "entrada-manual": ("[/", "\\]"), "base-de-datos": ("[(", ")]"), "demora": ("(", ")"),
            "almacenamiento": ("[\\", "/]"), "conector": ("((", "))"), "inspeccion": ("[[", "]]"),
            "operacion": ("((", "))"), "transporte": (">", "]")}
    out = ["```mermaid", "flowchart TB"]
    ids = []
    for i, p in enumerate(pasos):
        f = resolver_forma(p, juego)
        a, b = mapa.get(f, ("[", "]"))
        if minutos(p.get("espera", "")) > 0:
            out.append('  w%s(("espera %s"))' % (i, bonito(minutos(p["espera"]))))
            ids.append("w%s" % i)
        out.append('  n%s%s"%s"%s' % (i, a, p["paso"].replace('"', "'"), b))
        ids.append("n%s" % i)
    for a, b in zip(ids, ids[1:]):
        out.append("  %s --> %s" % (a, b))
    exc = [(i, p) for i, p in enumerate(pasos) if (p.get("excepcion") or "ninguna").lower() not in ("", "ninguna")]
    if exc:
        out += ["  subgraph rutas de excepcion", "    direction TB"]
        for i, p in exc:
            out.append('    e%s["%s: %s"]' % (i, p["excepcion"], p.get("ruta") or "sin ruta"))
            out.append("    n%s -.-> e%s" % (i, i))
        out.append("  end")
    out.append("```")
    return "\n".join(out)


def resumen(pasos, juego):
    cuenta = {}
    for p in pasos:
        f = resolver_forma(p, juego)
        cuenta.setdefault(f, [0, 0.0])
        cuenta[f][0] += 1
        cuenta[f][1] += minutos(p.get("trabajo", ""))
    demoras = [minutos(p.get("espera", "")) for p in pasos]
    return cuenta, sum(d for d in demoras if d > 0), sum(1 for d in demoras if d > 0)


CSS = (
    "@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Inter:wght@400;500;600&display=swap');\n"
    ":root{--accent:#2DD4BF;--text:#1A1A1A;--callout-bg:#F0FDF9;--callout-strong:#0F766E;--line:#1A1A1A;}\n"
    "*{margin:0;padding:0;box-sizing:border-box;}\n"
    "body{font-family:'Inter',system-ui,sans-serif;font-size:10pt;line-height:1.45;color:var(--text);background:#fff;width:216mm;margin:0 auto;padding:40pt 42pt;-webkit-print-color-adjust:exact;print-color-adjust:exact;}\n"
    "h1{font-family:'Montserrat',sans-serif;font-size:17pt;font-weight:700;letter-spacing:-.2pt;}\n"
    "h2{font-family:'Montserrat',sans-serif;font-size:10.5pt;font-weight:600;margin:15pt 0 6pt;text-transform:uppercase;letter-spacing:.6pt;}\n"
    ".sub{color:#4B5563;font-size:9pt;margin-top:3pt;}\n"
    ".rule{height:2pt;background:var(--accent);margin:10pt 0 14pt;}\n"
    ".hallazgo{background:var(--callout-bg);border-left:4pt solid var(--callout-strong);padding:9pt 11pt;font-size:10.5pt;}\n"
    ".contadores{display:flex;gap:10pt;margin:12pt 0 2pt;}\n"
    ".card{flex:1;border:1.4pt solid var(--line);border-radius:6pt;padding:8pt 10pt;}\n"
    ".card b{font-family:'Montserrat',sans-serif;font-size:17pt;display:block;line-height:1.1;}\n"
    ".card span{font-size:8.5pt;color:#4B5563;}\n"
    ".hoja{margin-top:10pt;break-inside:avoid;page-break-inside:avoid;}\n"
    ".hoja + .hoja{break-before:page;page-break-before:always;}\n"
    ".hoja h3{font-family:'Montserrat',sans-serif;font-size:9.5pt;font-weight:600;color:#4B5563;text-transform:uppercase;letter-spacing:.6pt;margin-bottom:2pt;}\n"
    ".diagrama{width:100%;height:auto;display:block;}\n"
    ".nodo{font-family:'Inter',sans-serif;font-size:13px;font-weight:600;fill:#1A1A1A;}\n"
    ".mini{font-family:'Inter',sans-serif;font-size:10px;fill:#6B7280;}\n"
    ".exc{font-family:'Inter',sans-serif;font-size:11px;font-weight:600;fill:#C2410C;}\n"
    ".demora{font-family:'Inter',sans-serif;font-size:11.5px;font-weight:600;fill:#B45309;}\n"
    ".carril{font-family:'Montserrat',sans-serif;font-size:10.5px;font-weight:600;fill:#374151;text-anchor:end;}\n"
    ".rama{font-family:'Inter',sans-serif;font-size:10.5px;font-weight:600;fill:#C2410C;}\n"
    "table{width:100%;border-collapse:collapse;font-size:9pt;}\n"
    "th,td{border:1pt solid var(--line);padding:4pt 6pt;text-align:left;vertical-align:top;}\n"
    "th{background:#F3F4F6;font-weight:600;}\n"
    ".pie{margin-top:14pt;border-top:1pt solid var(--line);padding-top:6pt;font-size:8pt;color:#4B5563;}\n"
    "@media print{body{width:100%;padding:26pt;} .no-print{display:none;} .diagrama{max-height:190mm;width:auto;margin:0 auto;}}\n"
    "@page{size:letter;margin:0;}\n"
    "@media screen{body{width:auto;max-width:100%;padding:22pt 20pt;} .hoja + .hoja{break-before:auto;page-break-before:auto;}}\n")



CAMPOS_FICHA = [("entradas", "a", "Entradas requeridas"), ("salidas", "a", "Salidas esperadas"),
                ("secuencia", "b", "Secuencia e interaccion"), ("criterios", "c", "Criterios y metodos"),
                ("recursos", "d", "Recursos necesarios"), ("responsables", "e", "Responsabilidades y autoridades"),
                ("riesgos", "g", "Riesgos y oportunidades"), ("mejora", "h", "Evaluacion y mejora")]


def ficha_html(meta):
    filas = ""
    for clave, letra, nombre in CAMPOS_FICHA:
        valor = (meta.get(clave) or "").strip()
        if valor:
            filas += "<tr><td><b>%s</b> (%s)</td><td>%s</td></tr>" % (nombre, letra, html.escape(valor))
    if not filas:
        return ""
    return '<h2>Ficha del proceso</h2><table><tr><th>Requisito de ISO 9001:2015, 4.4.1</th><th>Como se cumple aqui</th></tr>%s</table>' % filas


def entregable(pasos, meta, juego, por_pagina=7):
    svgs, _, _ = dibujar(pasos, meta, juego, por_pagina)
    cuenta, espera_total, n_demoras = resumen(pasos, juego)
    filas = "\n".join("<tr><td>%s</td><td>%d</td><td>%s</td></tr>" % (f, v[0], bonito(v[1])) for f, v in sorted(cuenta.items()))
    sinobs = sum(1 for p in pasos if clase_evidencia(p.get("evidencia", "")) not in SOLIDA)
    simb = "ISO 5807" if juego == "iso5807" else "cursograma OTIDA"
    hojas = []
    for i, s in enumerate(svgs):
        titulo = "Cómo camina el trabajo" if len(svgs) == 1 else "Cómo camina el trabajo, hoja %d de %d" % (i + 1, len(svgs))
        hojas.append('<div class="hoja"><h3>%s</h3>%s</div>' % (titulo, s))
    return "\n".join([
        "<!DOCTYPE html>", '<html lang="es-MX"><head><meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        "<title>Plano real: %s</title>" % html.escape(meta.get("proceso", "")),
        "<style>%s</style></head><body>" % CSS,
        "<h1>El plano real de la operación</h1>",
        '<div class="sub">%s · Proceso: %s · %s · Simbología: %s</div>' % (html.escape(meta.get("cliente", "")), html.escape(meta.get("proceso", "")), html.escape(meta.get("fase", "")), simb),
        '<div class="rule"></div>',
        '<div class="hallazgo">%s</div>' % html.escape(meta.get("hallazgo", "Sin hallazgo escrito todavía.")),
        ficha_html(meta),
        '<div class="contadores">',
        '<div class="card"><b>%d</b><span>pasos</span></div>' % len(pasos),
        '<div class="card"><b>%s</b><span>espera acumulada</span></div>' % bonito(espera_total),
        '<div class="card"><b>%d</b><span>esperas registradas</span></div>' % n_demoras,
        '<div class="card"><b>%d</b><span>pasos sin observar</span></div>' % sinobs,
        "</div>",
        "".join(hojas),
        "<h2>Resumen por símbolo</h2>",
        "<table><tr><th>Símbolo</th><th>Cantidad</th><th>Tiempo de trabajo</th></tr>%s</table>" % filas,
        '<div class="pie">Generado desde la tabla de pasos del expediente, con los símbolos de %s. El diagrama no se edita a mano: si la tabla cambia, se vuelve a generar. Lectura de rutas: linea solida, camino normal; linea punteada naranja con su condicion escrita, ruta de excepcion; la leyenda vuelve al paso N, retrabajo. Los pasos en gris punteado están sin observar y no sostienen un rediseño todavía.</div>' % simb,
        "</body></html>"])


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    nota = pathlib.Path(args[0])
    if not nota.exists():
        print("generar-diagrama: no existe la nota", nota)
        return 2
    juego = args[args.index("--set") + 1] if "--set" in args else "iso5807"
    por_pagina = int(args[args.index("--por-pagina") + 1]) if "--por-pagina" in args else 7
    if juego not in ("iso5807", "cursograma"):
        print("generar-diagrama: el juego de simbolos debe ser iso5807 o cursograma")
        return 2
    texto = nota.read_text(encoding="utf-8")
    pasos = leer_tabla(texto)
    if not pasos:
        print("generar-diagrama: no encontre la tabla de pasos en", nota)
        return 1
    meta = {}
    for etiqueta, clave in (("Cliente:", "cliente"), ("Proceso:", "proceso"), ("Fase:", "fase"), ("Hallazgo:", "hallazgo"),
                            ("Entradas:", "entradas"), ("Salidas:", "salidas"), ("Secuencia:", "secuencia"),
                            ("Criterios:", "criterios"), ("Recursos:", "recursos"), ("Responsables:", "responsables"),
                            ("Riesgos:", "riesgos"), ("Mejora:", "mejora")):
        m = re.search(re.escape(etiqueta) + r"\s*(.+)", texto)
        if m:
            meta[clave] = m.group(1).strip()
    svgs, cajas, altos = dibujar(pasos, meta, juego, por_pagina)
    choques = [c for pagina in cajas for c in colisiones(pagina)]
    desconocidas = sorted({(p.get("forma") or "").lower() for p in pasos if (p.get("forma") or "").lower() and (p.get("forma") or "").lower() not in FORMAS})
    der = mermaid(pasos, juego)
    if "--diagnostico" in args:
        cuenta, espera_total, n_demoras = resumen(pasos, juego)
        print("hojas: %d | alto de cada hoja: %s" % (len(svgs), [round(a) for a in altos]))
        print("formas:", dict((k, v[0]) for k, v in sorted(cuenta.items())))
        print("esperas: %d, total %s" % (n_demoras, bonito(espera_total)))
        print("traslapes:", choques if choques else "ninguno")
        # huecos entre formas consecutivas del eje, por hoja
        for i, pagina in enumerate(cajas):
            eje = sorted([b for b in pagina if b[4] != "excepcion"], key=lambda b: b[1])
            huecos = [round(eje[k + 1][1] - (eje[k][1] + eje[k][3])) for k in range(len(eje) - 1)]
            print("  hoja %d: %d formas, hueco minimo %s" % (i + 1, len(eje), min(huecos) if huecos else "-"))
        print("formas desconocidas:", desconocidas if desconocidas else "ninguna")
        return 1 if (choques or desconocidas) else 0
    if desconocidas:
        print("generar-diagrama: formas que no existen en el juego %s: %s" % (juego, ", ".join(desconocidas)))
        return 1
    if choques:
        print("generar-diagrama: el acomodo produce %d traslapes: %s" % (len(choques), choques[:3]))
        return 1
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
    cuenta, espera_total, n_demoras = resumen(pasos, juego)
    print("generar-diagrama: %d pasos en %d hojas | esperas %d (%s) | sin observar %d | traslapes 0" % (len(pasos), len(svgs), n_demoras, bonito(espera_total), sum(1 for p in pasos if clase_evidencia(p.get("evidencia", "")) not in SOLIDA)))
    if "--html" in args:
        salida = pathlib.Path(args[args.index("--html") + 1])
        salida.write_text(entregable(pasos, meta, juego, por_pagina), encoding="utf-8")
        print("generar-diagrama: entregable escrito en", salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
