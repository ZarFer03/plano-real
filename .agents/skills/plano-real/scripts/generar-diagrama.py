#!/usr/bin/env python3
"""Genera el diagrama del plano real desde el expediente.
La fuente son dos tablas: Nodos y Rutas. El dibujo es un grafo por capas: un nodo de
decision puede abrir dos o tres caminos, los caminos se separan y se vuelven a juntar,
y los retrabajos regresan por un carril exterior. Nunca se edita a mano.

Si la nota todavia trae la tabla vieja de pasos, se sintetiza un grafo lineal con sus
rutas de excepcion, para no romper expedientes anteriores.

Uso:
  python3 generar-diagrama.py 04_plano-real.md                      escribe el bloque Mermaid en la nota
  python3 generar-diagrama.py 04_plano-real.md --html salida.html   emite ademas el entregable
  python3 generar-diagrama.py 04_plano-real.md --check              sale 1 si el diagrama de la nota quedo viejo
  python3 generar-diagrama.py 04_plano-real.md --diagnostico        reporta cruces, traslapes y resumen
  --set iso5807 | cursograma      juego de simbolos
  --por-hoja N                    altura maxima de cada hoja
"""
import html
import pathlib
import re
import sys

INICIO, FIN = "<!-- diagrama:inicio -->", "<!-- diagrama:fin -->"
SOLIDA = {"observado", "medido", "firmado"}
LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# forma: (alto base, ancho minimo, factor de ancho sobre el texto, caracteres por linea)
FORMAS = {
    "inicio": (46, 170, 1.0, 30), "fin": (46, 170, 1.0, 30),
    "actividad": (56, 190, 1.0, 30), "documento": (64, 190, 1.0, 30),
    "datos": (56, 190, 1.0, 28), "entrada-manual": (56, 190, 1.0, 26),
    "base-de-datos": (70, 190, 1.0, 28), "almacenamiento": (56, 190, 1.0, 26),
    "preparacion": (56, 200, 1.0, 26), "subproceso": (56, 190, 1.0, 28),
    "conector": (50, 50, 1.0, 4), "demora": (46, 150, 1.0, 18),
    "decision": (104, 240, 1.75, 22), "operacion": (92, 150, 1.0, 18),
    "inspeccion": (92, 150, 1.0, 18), "transporte": (56, 190, 1.0, 26),
}
ANCHO_CHAR = 7.7
SEP_Y, SEP_X = 78, 46
CANAL_X, MARGEN_X, MARGEN_Y = 26, 60, 40


def leer_secciones(texto):
    meta, tablas = {}, {}
    for etiqueta, clave in (("Cliente:", "cliente"), ("Proceso:", "proceso"), ("Fase:", "fase"), ("Hallazgo:", "hallazgo"),
                            ("Entradas:", "entradas"), ("Salidas:", "salidas"), ("Secuencia:", "secuencia"),
                            ("Criterios:", "criterios"), ("Recursos:", "recursos"), ("Responsables:", "responsables"),
                            ("Riesgos:", "riesgos"), ("Mejora:", "mejora")):
        m = re.search(re.escape(etiqueta) + r"\s*(.+)", texto)
        if m:
            meta[clave] = m.group(1).strip()
    encabezado, filas, destino = None, [], None
    for linea in texto.split("\n"):
        l = linea.strip()
        if not l.startswith("|"):
            if encabezado:
                tablas[destino] = tablas.get(destino, []) + filas
            encabezado, filas, destino = None, [], None
            continue
        celdas = [c.strip() for c in l.strip("|").split("|")]
        if set("".join(celdas)) <= set("-: "):
            continue
        if encabezado is None:
            encabezado = [c.lower() for c in celdas]
            if "hacia" in encabezado and "desde" in encabezado:
                destino = "rutas"
            elif "hacia" in encabezado:
                destino = "rutas"
            elif "forma" in encabezado or "texto" in encabezado:
                destino = "nodos"
            else:
                destino = "pasos"
            continue
        filas.append({k: "" for k in encabezado} | {encabezado[i]: c for i, c in enumerate(celdas) if i < len(encabezado)})
    if encabezado:
        tablas[destino] = tablas.get(destino, []) + filas
    return meta, tablas


def minutos(t):
    m = re.match(r"([\d.]+)\s*(min|h|horas?|d|dias?|días?)", (t or "").strip(), re.I)
    if not m:
        return 0.0
    v = float(m.group(1))
    u = m.group(2).lower()
    return v * 60 if u.startswith("h") else (v if u.startswith("min") else v * 1440)


def bonito(m):
    if m >= 1440 and m % 1440 == 0:
        return "%g d" % (m / 1440)
    return ("%g h" % (m / 60)) if m >= 60 else ("%g min" % m)


def clase_evidencia(c):
    c = (c or "").lower()
    for k in ("observado", "medido", "firmado"):
        if k in c:
            return k
    return "dicho" if "dicho" in c else "sin observar"


def resolver_forma(fila, juego):
    f = (fila.get("forma") or "").strip().lower()
    if f in FORMAS:
        return f
    if (fila.get("tipo") or "").lower().startswith("decid"):
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


def grafo(meta, tablas):
    """Devuelve nodos y rutas. Si la nota trae la tabla vieja de pasos, sintetiza el grafo."""
    nodos, rutas = [], []
    if tablas.get("nodos"):
        for fila in tablas["nodos"]:
            nid = (fila.get("id") or fila.get("nodo") or "").strip()
            if not nid:
                continue
            nodos.append({"id": nid, "texto": (fila.get("texto") or fila.get("paso") or "").strip(), "fila": fila,
                          "quien": (fila.get("quien") or "").strip(), "sistema": (fila.get("sistema") or "").strip(),
                          "trabajo": (fila.get("trabajo") or "").strip(), "espera": (fila.get("espera") or "").strip(),
                          "evidencia": (fila.get("evidencia") or "").strip()})
        for fila in tablas.get("rutas", []):
            d, h = (fila.get("desde") or "").strip(), (fila.get("hacia") or "").strip()
            if d and h:
                rutas.append({"desde": d, "hacia": h, "etiqueta": (fila.get("etiqueta") or fila.get("condicion") or "").strip(),
                              "tipo": (fila.get("tipo") or "normal").strip().lower()})
        return nodos, rutas
    pasos = tablas.get("pasos") or []
    nodos.append({"id": "n0", "texto": "Inicio del caso", "fila": {"forma": "inicio", "quien": ""}, "quien": "", "sistema": "", "trabajo": "", "espera": "", "evidencia": ""})
    for i, p in enumerate(pasos, 1):
        nodos.append({"id": "n%d" % i, "texto": p.get("paso", ""), "fila": p, "quien": p.get("quien", ""), "sistema": p.get("sistema", ""),
                      "trabajo": p.get("trabajo", ""), "espera": p.get("espera", ""), "evidencia": p.get("evidencia", "")})
        rutas.append({"desde": "n%d" % (i - 1), "hacia": "n%d" % i, "etiqueta": "", "tipo": "normal"})
        exc = (p.get("excepcion") or "").strip()
        if exc and exc.lower() != "ninguna":
            eid = "e%d" % i
            nodos.append({"id": eid, "texto": exc, "fila": {"forma": "actividad", "quien": p.get("quien", "")}, "quien": p.get("quien", ""),
                          "sistema": "", "trabajo": "", "espera": "", "evidencia": p.get("evidencia", "")})
            rutas.append({"desde": "n%d" % i, "hacia": eid, "etiqueta": (p.get("condicion") or "").strip() or "excepcion", "tipo": "excepcion"})
            regreso = (p.get("regreso") or "").strip()
            destino = ("n%s" % regreso) if regreso.isdigit() else "n%d" % (i + 1)
            rutas.append({"desde": eid, "hacia": destino, "etiqueta": ("vuelve al paso %s" % regreso) if regreso.isdigit() else "continua", "tipo": "retrabajo"})
    nodos.append({"id": "nf", "texto": "Fin del caso", "fila": {"forma": "fin", "quien": ""}, "quien": "", "sistema": "", "trabajo": "", "espera": "", "evidencia": ""})
    rutas.append({"desde": "n%d" % len(pasos), "hacia": "nf", "etiqueta": "", "tipo": "normal"})
    return nodos, rutas


def medir(texto, forma):
    alto, minimo, factor, chars = FORMAS.get(forma, FORMAS["actividad"])
    lineas = wrap(texto, chars)
    ancho = max(len(l) for l in lineas) * ANCHO_CHAR * factor + 44
    ancho = max(ancho, minimo * factor)
    return min(ancho, 360 * factor), alto, lineas


def capas(nodos, rutas):
    """Rango por camino mas largo; las aristas que cierran ciclo se marcan como retorno."""
    ids = [n["id"] for n in nodos]
    salidas = {i: [] for i in ids}
    entradas = {i: [] for i in ids}
    for r in rutas:
        if r["desde"] in salidas and r["hacia"] in entradas:
            salidas[r["desde"]].append(r)
            entradas[r["hacia"]].append(r)
    inicio = next((n["id"] for n in nodos if (n["fila"].get("forma") or "").strip().lower() == "inicio"), None)
    if inicio is None:
        inicio = next((i for i in ids if not entradas[i]), ids[0] if ids else None)
    color, retorno = {}, set()
    pila = []

    def dfs(u):
        color[u] = 1
        pila.append(u)
        for r in salidas[u]:
            v = r["hacia"]
            if color.get(v) == 1:
                retorno.add((r["desde"], r["hacia"], r["etiqueta"]))
            elif v not in color:
                dfs(v)
        pila.pop()
        color[u] = 2

    if inicio:
        dfs(inicio)
    for i in ids:
        if i not in color:
            dfs(i)
    rango = {i: 0 for i in ids}
    for _ in range(len(ids) + 1):
        cambio = False
        for r in rutas:
            if (r["desde"], r["hacia"], r["etiqueta"]) in retorno:
                continue
            if r["desde"] in rango and r["hacia"] in rango:
                if rango[r["hacia"]] < rango[r["desde"]] + 1:
                    rango[r["hacia"]] = rango[r["desde"]] + 1
                    cambio = True
        if not cambio:
            break
    por_rango = {}
    orden = {n["id"]: k for k, n in enumerate(nodos)}
    for i in ids:
        por_rango.setdefault(rango[i], []).append(i)
    for k in por_rango:
        por_rango[k].sort(key=lambda i: orden[i])
    return rango, por_rango, salidas, entradas, retorno, inicio


def ordenar_filas(por_rango, salidas, entradas, vueltas=6):
    pos = {}
    for k, fila in por_rango.items():
        for j, i in enumerate(fila):
            pos[i] = (k, j)

    def mediana(vecinos):
        v = sorted(pos[j][1] for j in vecinos if j in pos and pos[j][0] != pos.get(i, (0, 0))[0])
        return v[len(v) // 2] if v else pos[i][1]

    for n in range(vueltas):
        orden_k = sorted(por_rango)
        for k in (orden_k if n % 2 == 0 else list(reversed(orden_k))):
            for i in por_rango[k]:
                vecinos = [r["hacia"] for r in salidas[i]] + [r["desde"] for r in entradas[i]]
                pos[i] = (k, mediana(vecinos))
            por_rango[k].sort(key=lambda i: pos[i][1])
            for j, i in enumerate(por_rango[k]):
                pos[i] = (k, j)
    return por_rango


def acomodar(nodos, rutas, juego):
    rango, por_rango, salidas, entradas, retorno, inicio = capas(nodos, rutas)
    por_rango = ordenar_filas(por_rango, salidas, entradas)
    figura = {}
    for n in nodos:
        forma = resolver_forma(n["fila"], juego)
        ancho, alto, lineas = medir(n["texto"], forma)
        figura[n["id"]] = {"n": n, "forma": forma, "ancho": ancho, "alto": alto, "lineas": lineas}
    alto_fila = {k: max(figura[i]["alto"] for i in fila) for k, fila in por_rango.items()}
    y = MARGEN_Y
    for k in sorted(por_rango):
        for i in por_rango[k]:
            figura[i]["y"] = y + (alto_fila[k] - figura[i]["alto"]) / 2
        y += alto_fila[k] + SEP_Y
    ancho_por_fila = {}
    for k, fila in por_rango.items():
        total = sum(figura[i]["ancho"] for i in fila) + SEP_X * (len(fila) - 1)
        ancho_por_fila[k] = total
    ancho = max(ancho_por_fila.values()) if ancho_por_fila else 600
    centro = MARGEN_X + ancho / 2
    for k, fila in por_rango.items():
        x = centro - ancho_por_fila[k] / 2
        for i in fila:
            figura[i]["x"] = x
            x += figura[i]["ancho"] + SEP_X
    retornos = sorted({(r["desde"], r["hacia"]) for r in rutas if (r["desde"], r["hacia"], r["etiqueta"]) in retorno},
                      key=lambda p: (rango.get(p[1], 0), rango.get(p[0], 0)))
    carril = {}
    base = MARGEN_X + ancho + CANAL_X
    for k, (d, h) in enumerate(retornos):
        carril[(d, h)] = base + k * 34
    derecha = base + max(0, len(retornos) - 1) * 34
    for r in rutas:
        if (r["desde"], r["hacia"]) in carril and r.get("etiqueta"):
            derecha = max(derecha, carril[(r["desde"], r["hacia"])] + 10 + len(r["etiqueta"]) * 6.1 + 30)
    ancho_total = max(base + max(1, len(retornos)) * 34 + MARGEN_X, derecha + 20)
    return figura, rango, por_rango, salidas, entradas, retorno, carril, ancho_total, y


def puntos_arista(figura, r, rango, retorno, carril):
    """Devuelve los puntos de la ruta y el punto donde va la etiqueta."""
    s, t = figura[r["desde"]], figura[r["hacia"]]
    if r.get("sintetica"):
        mx, my = s["x"] + s["ancho"] / 2, s["y"] + s["alto"]
        tx, ty = t["x"] + t["ancho"] / 2, t["y"]
        if abs(mx - tx) < 2:
            return [(mx, my), (tx, ty)], (mx + 8, (my + ty) / 2), False
        medio = my + (ty - my) / 2
        return [(mx, my), (mx, medio), (tx, medio), (tx, ty)], ((mx + tx) / 2, medio - 7), False
    retorno_arista = (r["desde"], r["hacia"], r["etiqueta"]) in retorno or rango[r["hacia"]] <= rango[r["desde"]]
    mx, my = s["x"] + s["ancho"] / 2, s["y"] + s["alto"]
    if retorno_arista:
        canal = carril.get((r["desde"], r["hacia"]))
        if canal is None:
            canal = max(carril.values()) if carril else MARGEN_X + 600
        salida_y = s["y"] + s["alto"] + SEP_Y * 0.34
        llegada_y = max(16.0, t["y"] - SEP_Y * 0.34)
        pts = [(mx, s["y"] + s["alto"]), (mx, salida_y), (canal, salida_y), (canal, llegada_y),
               (t["x"] + t["ancho"] / 2 + 16, llegada_y), (t["x"] + t["ancho"] / 2 + 16, t["y"])]
        return pts, (canal + 10, (salida_y + llegada_y) / 2 + 4), True
    tx, ty = t["x"] + t["ancho"] / 2, t["y"]
    if abs(mx - tx) < 2:
        return [(mx, my), (tx, ty)], (mx + 8, (my + ty) / 2), False
    medio = my + (ty - my) / 2
    pts = [(mx, my), (mx, medio), (tx, medio), (tx, ty)]
    return pts, ((mx + tx) / 2, medio - 7), False


def forma_svg(f, x, y, w, h, solida):
    borde = "#1A1A1A" if solida else "#9CA3AF"
    dash = "" if solida else ' stroke-dasharray="6 4"'
    relleno = "#FFFFFF" if solida else "#F3F4F6"
    a = 'fill="%s" stroke="%s" stroke-width="2"%s' % (relleno, borde, dash)
    cx, cy = x + w / 2, y + h / 2
    if f in ("inicio", "fin"):
        return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" %s/>' % (x, y, w, h, h / 2, a)
    if f in ("actividad", "subproceso"):
        s = '<rect x="%s" y="%s" width="%s" height="%s" rx="4" %s/>' % (x, y, w, h, a)
        if f == "subproceso":
            s += '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="2"/><line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="2"/>' % (x + 18, y, x + 18, y + h, borde, x + w - 18, y, x + w - 18, y + h, borde)
        return s
    if f == "preparacion":
        return '<polygon points="%s,%s %s,%s %s,%s %s,%s %s,%s %s,%s" %s/>' % (x + 18, y, x + w - 18, y, x + w, cy, x + w - 18, y + h, x + 18, y + h, x, cy, a)
    if f == "decision":
        return '<polygon points="%s,%s %s,%s %s,%s %s,%s" %s/>' % (cx, y, x + w, cy, cx, y + h, x, cy, a)
    if f == "datos":
        return '<polygon points="%s,%s %s,%s %s,%s %s,%s" %s/>' % (x + 20, y, x + w, y, x + w - 20, y + h, x, y + h, a)
    if f == "entrada-manual":
        return '<polygon points="%s,%s %s,%s %s,%s %s,%s" %s/>' % (x + 22, y, x + w, y + 14, x + w, y + h, x, y + h, a)
    if f == "documento":
        d = "M%s,%s H%s V%s C%s,%s %s,%s %s,%s H%s Z" % (x, y, x + w, y + h - 13, x + w * .75, y + h + 7, x + w * .25, y + h - 24, x, y + h - 5, x)
        return '<path d="%s" %s/>' % (d, a)
    if f == "almacenamiento":
        return '<polygon points="%s,%s %s,%s %s,%s" %s/>' % (x, y, x + w, y, cx, y + h, a)
    if f == "base-de-datos":
        ry = 9
        return '<path d="M%s,%s V%s A%s,%s 0 0 0 %s,%s V%s A%s,%s 0 0 0 %s,%s Z" %s/>' % (x, y + ry, y + h - ry, w / 2, ry, x + w, y + h - ry, y + ry, w / 2, ry, x, y + ry, a)
    if f == "transporte":
        return '<polygon points="%s,%s %s,%s %s,%s %s,%s %s,%s %s,%s" %s/>' % (x, y, x + w - 28, y, x + w - 28, y - 8, x + w, cy, x + w - 28, y + h + 8, x + w - 28, y + h, a)
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" %s/>' % (cx, cy, w / 2, h / 2, a)


ESTILO_ARISTA = {"normal": ("#1A1A1A", ""), "excepcion": ("#C2410C", ' stroke-dasharray="6 4"'),
                 "retrabajo": ("#1D4ED8", ' stroke-dasharray="6 4"'), "rechazo": ("#B91C1C", ' stroke-dasharray="2 3"')}


def dibujar_hoja(figura, ids, rango, rutas, retorno, carril, alto, titulo, primera, ultima, letra_antes, letra_siguiente, bboxes, ancho=1200):
    partes = ['<svg viewBox="0 0 %g %g" xmlns="http://www.w3.org/2000/svg" class="diagrama">' % (ancho, alto),
              '<defs>' + "".join(
                  '<marker id="flecha%s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>' % (k, c)
                  for k, (c, d) in ESTILO_ARISTA.items()) + '</defs>']
    for r in rutas:
        if r["desde"] not in ids or r["hacia"] not in ids:
            continue
        color, dash = ESTILO_ARISTA.get(r["tipo"], ESTILO_ARISTA["normal"])
        pts, (lx, ly), es_retorno = puntos_arista(figura, r, rango, retorno, carril)
        d = "M" + " L".join("%.1f,%.1f" % p for p in pts)
        partes.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"%s marker-end="url(#flecha%s)"/>' % (d, color, dash, r["tipo"] if r["tipo"] in ESTILO_ARISTA else "normal"))
        if r["etiqueta"]:
            ancho_et = len(r["etiqueta"]) * 6.1 + 10
            partes.append('<rect x="%.1f" y="%.1f" width="%.1f" height="15" rx="3" fill="#FFFFFF"/>' % (lx - 5, ly - 11, ancho_et))
            partes.append('<text x="%.1f" y="%.1f" class="etiqueta-ruta">%s</text>' % (lx, ly, html.escape(r["etiqueta"])))
    for i in ids:
        f = figura[i]
        n, solida = f["n"], clase_evidencia(f["n"]["evidencia"]) in SOLIDA or f["forma"] in ("inicio", "fin")
        partes.append(forma_svg(f["forma"], f["x"], f["y"], f["ancho"], f["alto"], solida))
        bboxes.append((f["x"], f["y"], f["ancho"], f["alto"], f["forma"]))
        num = re.match(r"n?(\d+)$", i)
        etiqueta = ("%s · %s" % (num.group(1), f["n"]["texto"])) if num else f["n"]["texto"]
        lineas = wrap(etiqueta, FORMAS.get(f["forma"], FORMAS["actividad"])[3])
        if f["forma"] == "decision":
            partes += ['<text x="%.1f" y="%.1f" class="nodo" text-anchor="middle">%s</text>' % (f["x"] + f["ancho"] / 2, f["y"] + f["alto"] / 2 - 6 * (len(lineas) - 1) + 4, html.escape(l))
                       for l in lineas]
        elif f["forma"] == "conector":
            partes.append('<text x="%.1f" y="%.1f" class="nodo" text-anchor="middle">%s</text>' % (f["x"] + f["ancho"] / 2, f["y"] + f["alto"] / 2 + 5, html.escape(lineas[0])))
        else:
            partes += ['<text x="%.1f" y="%.1f" class="nodo">%s</text>' % (f["x"] + 16, f["y"] + 26 + 16 * k, html.escape(l)) for k, l in enumerate(lineas)]
        pie = " · ".join(x for x in [(f["n"]["quien"] or "").strip(), (f["n"]["sistema"] or "").strip()] if x)
        espera = minutos(f["n"]["espera"])
        if espera > 0:
            pie = ("espera %s · " % bonito(espera)) + pie
        if pie and f["forma"] == "decision":
            partes.append('<text x="%.1f" y="%.1f" class="mini" text-anchor="middle">%s</text>' % (f["x"] + f["ancho"] / 2, f["y"] + f["alto"] - 12, html.escape(pie[:34])))
        elif pie:
            partes.append('<text x="%.1f" y="%.1f" class="mini">%s</text>' % (f["x"] + 16, f["y"] + f["alto"] - 12, html.escape(pie[:38])))
    partes.append("</svg>")
    return "\n".join(partes)


def hoja_titulo(meta, i, total):
    base = "Cómo camina el trabajo"
    return base if total == 1 else "%s, hoja %d de %d" % (base, i + 1, total)


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
    ".etiqueta-ruta{font-family:'Inter',sans-serif;font-size:11px;font-weight:600;fill:#374151;}\n"
    "table{width:100%;border-collapse:collapse;font-size:9pt;}\n"
    "th,td{border:1pt solid var(--line);padding:4pt 6pt;text-align:left;vertical-align:top;}\n"
    "th{background:#F3F4F6;font-weight:600;}\n"
    ".leyenda{display:flex;gap:14pt;font-size:8.5pt;color:#374151;margin:6pt 0 4pt;flex-wrap:wrap;}\n"
    ".leyenda b{font-weight:600;}\n"
    ".sw{display:inline-block;width:22pt;height:0;border-top:2pt solid #1A1A1A;vertical-align:middle;margin-right:3pt;}\n"
    ".sw.exc{border-top-style:dashed;border-color:#C2410C;}\n"
    ".sw.ret{border-top-style:dashed;border-color:#1D4ED8;}\n"
    ".sw.rech{border-top-style:dotted;border-color:#B91C1C;}\n"
    ".pie{margin-top:14pt;border-top:1pt solid var(--line);padding-top:6pt;font-size:8pt;color:#4B5563;}\n"
    "@media print{body{width:100%;padding:26pt;} .diagrama{max-height:200mm;width:auto;max-width:100%;margin:0 auto;}}\n"
    "@page{size:letter;margin:0;}\n"
    "@media screen{body{width:auto;max-width:100%;padding:22pt 20pt;} .hoja + .hoja{break-before:auto;page-break-before:auto;}}\n")


def ficha_html(meta):
    campos = [("entradas", "a", "Entradas requeridas"), ("salidas", "a", "Salidas esperadas"),
              ("secuencia", "b", "Secuencia e interacción"), ("criterios", "c", "Criterios y métodos"),
              ("recursos", "d", "Recursos necesarios"), ("responsables", "e", "Responsabilidades y autoridades"),
              ("riesgos", "g", "Riesgos y oportunidades"), ("mejora", "h", "Evaluación y mejora")]
    filas = "".join("<tr><td><b>%s</b> (%s)</td><td>%s</td></tr>" % (nombre, letra, html.escape(meta[clave]))
                    for clave, letra, nombre in campos if meta.get(clave))
    return ('<h2>Ficha del proceso</h2><table><tr><th>Requisito de ISO 9001:2015, 4.4.1</th><th>Cómo se cumple aquí</th></tr>%s</table>' % filas) if filas else ""


def entregable(nodos, rutas, meta, juego, figura, rango, hojas, alto_total):
    cuenta, espera_total, n_demoras = resumen(nodos, juego)
    filas = "".join("<tr><td>%s</td><td>%d</td><td>%s</td></tr>" % (f, v[0], bonito(v[1])) for f, v in sorted(cuenta.items()))
    sinobs = sum(1 for n in nodos if clase_evidencia(n["evidencia"]) not in SOLIDA)
    decisiones = [n for n in nodos if resolver_forma(n["fila"], juego) == "decision"]
    salidas = {}
    for r in rutas:
        salidas[r["desde"]] = salidas.get(r["desde"], 0) + 1
    ramas = sum(1 for d in decisiones if salidas.get(d["id"], 0) >= 2)
    retrabajos = sum(1 for r in rutas if r["tipo"] == "retrabajo")
    simb = "ISO 5807" if juego == "iso5807" else "cursograma OTIDA"
    cuerpo = "".join('<div class="hoja"><h3>%s</h3>%s</div>' % (hoja_titulo(meta, i, len(hojas)), s) for i, s in enumerate(hojas))
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
        '<div class="card"><b>%d</b><span>nodos</span></div>' % len(nodos),
        '<div class="card"><b>%d</b><span>decisiones con dos o más salidas</span></div>' % ramas,
        '<div class="card"><b>%d</b><span>rutas de retrabajo</span></div>' % retrabajos,
        '<div class="card"><b>%s</b><span>espera acumulada</span></div>' % bonito(espera_total),
        "</div>",
        '<div class="leyenda"><span><i class="sw"></i>camino normal</span><span><i class="sw exc"></i>ruta de excepción</span><span><i class="sw ret"></i>retrabajo, vuelve a un paso anterior</span><span><i class="sw rech"></i>rechazo o cierre terminal</span></div>',
        cuerpo,
        "<h2>Resumen por símbolo</h2>",
        "<table><tr><th>Símbolo</th><th>Cantidad</th><th>Tiempo de trabajo</th></tr>%s</table>" % filas,
        '<div class="pie">Generado desde las tablas de nodos y rutas del expediente, con los símbolos de %s. El diagrama no se edita a mano: si las tablas cambian, se vuelve a generar. Cada rombo declara su condición en la ruta que sale de él. Los nodos en gris punteado están sin observar y no sostienen un rediseño todavía. Pasos sin observar: %d.</div>' % (simb, sinobs),
        "</body></html>"])


def mermaid(nodos, rutas, juego):
    mapa = {"inicio": ("([", "])"), "fin": ("([", "])"), "actividad": ("[", "]"), "subproceso": ("[[", "]]"),
            "preparacion": ("{{", "}}"), "decision": ("{", "}"), "datos": ("[/", "/]"), "documento": ("[/", "\\]"),
            "entrada-manual": ("[/", "\\]"), "base-de-datos": ("[(", ")]"), "demora": ("(", ")"),
            "almacenamiento": ("[\\", "/]"), "conector": ("((", "))"), "inspeccion": ("[[", "]]"),
            "operacion": ("((", "))"), "transporte": (">", "]")}
    out = ["```mermaid", "flowchart TB"]
    for n in nodos:
        a, b = mapa.get(resolver_forma(n["fila"], juego), ("[", "]"))
        out.append('  %s%s"%s"%s' % (n["id"], a, n["texto"].replace('"', "'"), b))
    for r in rutas:
        flecha = " -.-> " if r["tipo"] != "normal" else " --> "
        etiqueta = ("|%s|" % r["etiqueta"].replace("|", "/")) if r["etiqueta"] else ""
        out.append("  %s%s%s%s" % (r["desde"], flecha, etiqueta, r["hacia"]))
    out.append("```")
    return "\n".join(out)


def resumen(nodos, juego):
    cuenta = {}
    for n in nodos:
        f = resolver_forma(n["fila"], juego)
        cuenta.setdefault(f, [0, 0.0])
        cuenta[f][0] += 1
        cuenta[f][1] += minutos(n["trabajo"])
    demoras = [minutos(n["espera"]) for n in nodos]
    return cuenta, sum(d for d in demoras if d > 0), sum(1 for d in demoras if d > 0)


def choques(bboxes):
    fallas = []
    for i in range(len(bboxes)):
        for j in range(i + 1, len(bboxes)):
            ax, ay, aw, ah, an = bboxes[i]
            bx, by, bw, bh, bn = bboxes[j]
            if ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah:
                fallas.append((an, bn))
    return fallas


def cruces(figura, ids, rutas, rango, retorno, carril):
    """Detecta aristas que atraviesan una forma que no es su origen ni su destino."""
    fallas = []
    for r in rutas:
        if r["desde"] not in ids or r["hacia"] not in ids:
            continue
        pts, _, _ = puntos_arista(figura, r, rango, retorno, carril)
        for k in range(len(pts) - 1):
            (x1, y1), (x2, y2) = pts[k], pts[k + 1]
            for i in ids:
                if i in (r["desde"], r["hacia"]):
                    continue
                f = figura[i]
                if x1 == x2:
                    if f["x"] < x1 < f["x"] + f["ancho"] and min(y1, y2) < f["y"] + f["alto"] and f["y"] < max(y1, y2):
                        fallas.append((r["desde"], r["hacia"], i))
                elif y1 == y2:
                    if f["y"] < y1 < f["y"] + f["alto"] and min(x1, x2) < f["x"] + f["ancho"] and f["x"] < max(x1, x2):
                        fallas.append((r["desde"], r["hacia"], i))
    return fallas


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
    if juego not in ("iso5807", "cursograma"):
        print("generar-diagrama: el juego de simbolos debe ser iso5807 o cursograma")
        return 2
    limite = int(args[args.index("--por-hoja") + 1]) if "--por-hoja" in args else 1150
    texto = nota.read_text(encoding="utf-8")
    meta, tablas = leer_secciones(texto)
    nodos, rutas = grafo(meta, tablas)
    if not nodos:
        print("generar-diagrama: no encontre nodos ni tabla de pasos en", nota)
        return 1
    figura, rango, por_rango, salidas, entradas, retorno, carril, ancho, alto_total = acomodar(nodos, rutas, juego)
    desconocidas = sorted({(n["fila"].get("forma") or "").lower() for n in nodos if (n["fila"].get("forma") or "").lower() and (n["fila"].get("forma") or "").lower() not in FORMAS})
    hojas, bboxes_por_hoja, rangos_hoja = [], [], []
    actual, alto_actual = [], 0
    for k in sorted(por_rango):
        alto_k = max(figura[i]["alto"] for i in por_rango[k]) + SEP_Y
        if actual and alto_actual + alto_k > limite:
            rangos_hoja.append(actual)
            actual, alto_actual = [], 0
        actual.append(k)
        alto_actual += alto_k
    if actual:
        rangos_hoja.append(actual)
    pagina = {}
    for idx, ks in enumerate(rangos_hoja):
        for k in ks:
            for i in por_rango[k]:
                pagina[i] = idx
    sinteticas = {}
    usados = {}
    for r in rutas:
        pd, ph = pagina.get(r["desde"]), pagina.get(r["hacia"])
        if pd is None or ph is None or pd == ph:
            continue
        src, dst = figura[r["desde"]], figura[r["hacia"]]
        for idx, letra, es_salida in ((pd, LETRAS[ph], True), (ph, LETRAS[pd], False)):
            if es_salida:
                sid = "c%s%s" % (r["desde"], LETRAS[ph])
                sy = src["y"] + src["alto"] + 14
                sx = src["x"] + src["ancho"] / 2 - 25
            else:
                sid = "c%s%s" % (r["hacia"], LETRAS[pd])
                sy = max(6.0, dst["y"] - 58)
                sx = dst["x"] + dst["ancho"] / 2 - 25
            usados[(idx, sid)] = usados.get((idx, sid), 0) + 1
            sx += 66 * (usados[(idx, sid)] - 1)
            figura[sid] = {"n": {"id": sid, "texto": letra, "fila": {"forma": "conector"}, "quien": "", "sistema": "", "trabajo": "", "espera": "", "evidencia": "observado"},
                           "forma": "conector", "ancho": 50, "alto": 50, "lineas": [letra], "x": sx, "y": sy}
            sinteticas.setdefault(idx, {"nodos": [], "rutas": []})
            if sid not in sinteticas[idx]["nodos"]:
                sinteticas[idx]["nodos"].append(sid)
            if es_salida:
                sinteticas[idx]["rutas"].append({"desde": r["desde"], "hacia": sid, "etiqueta": "continua en la hoja %s" % LETRAS[ph], "tipo": r["tipo"], "sintetica": True})
            else:
                sinteticas[idx]["rutas"].append({"desde": sid, "hacia": r["hacia"], "etiqueta": "viene de la hoja %s" % LETRAS[pd], "tipo": r["tipo"], "sintetica": True})
    for idx, ks in enumerate(rangos_hoja):
        ids = [i for k in ks for i in por_rango[k]] + sinteticas.get(idx, {}).get("nodos", [])
        base = min(figura[i]["y"] for i in ids) - 70
        for i in ids:
            figura[i]["y"] -= base
        alto = max(figura[i]["y"] + figura[i]["alto"] for i in ids) + 80
        rutas_hoja = [dict(r) for r in rutas if r["desde"] in ids and r["hacia"] in ids] + sinteticas.get(idx, {}).get("rutas", [])
        bboxes = []
        s = dibujar_hoja(figura, ids, rango, rutas_hoja, retorno, carril, alto, "", idx == 0, idx == len(rangos_hoja) - 1, LETRAS[idx - 1] if idx else "", LETRAS[idx] if idx < len(rangos_hoja) - 1 else "", bboxes, ancho)
        hojas.append(s)
        bboxes_por_hoja.append(bboxes)
        for i in ids:
            figura[i]["y"] += base
    choques_totales = [c for pagina in bboxes_por_hoja for c in choques(pagina)]
    cruces_totales = cruces(figura, [n["id"] for n in nodos], rutas, rango, retorno, carril)
    der = mermaid(nodos, rutas, juego)
    if "--diagnostico" in args:
        cuenta, espera_total, n_demoras = resumen(nodos, juego)
        salidas_n = {}
        for r in rutas:
            salidas_n[r["desde"]] = salidas_n.get(r["desde"], 0) + 1
        decisiones = [n["id"] for n in nodos if resolver_forma(n["fila"], juego) == "decision"]
        print("nodos: %d | rutas: %d | hojas: %d" % (len(nodos), len(rutas), len(hojas)))
        print("capas: %d | ancho del dibujo: %d | alto: %d" % (len(por_rango), ancho, alto_total))
        print("formas:", dict((k, v[0]) for k, v in sorted(cuenta.items())))
        print("decisiones: %d, con dos o mas salidas: %d" % (len(decisiones), sum(1 for d in decisiones if salidas_n.get(d, 0) >= 2)))
        print("rutas de retrabajo:", sum(1 for r in rutas if r["tipo"] == "retrabajo"), "| de excepcion:", sum(1 for r in rutas if r["tipo"] == "excepcion"), "| de rechazo:", sum(1 for r in rutas if r["tipo"] == "rechazo"))
        print("esperas: %d, total %s" % (n_demoras, bonito(espera_total)))
        print("traslapes:", choques_totales if choques_totales else "ninguno")
        print("rutas que atraviesan una forma:", sorted(set(cruces_totales)) if cruces_totales else "ninguna")
        print("formas desconocidas:", desconocidas if desconocidas else "ninguna")
        return 1 if (choques_totales or cruces_totales or desconocidas) else 0
    if desconocidas:
        print("generar-diagrama: formas que no existen en el juego %s: %s" % (juego, ", ".join(desconocidas)))
        return 1
    if choques_totales:
        print("generar-diagrama: el acomodo produce %d traslapes: %s" % (len(choques_totales), choques_totales[:3]))
        return 1
    if "--check" in args:
        actual = re.search(re.escape(INICIO) + r"(.*?)" + re.escape(FIN), texto, re.S)
        if not actual or actual.group(1).strip() != der.strip():
            print("generar-diagrama: el diagrama de la nota no coincide con las tablas de nodos y rutas")
            return 1
        print("generar-diagrama: el diagrama esta al dia")
        return 0
    bloque = INICIO + "\n" + der + "\n" + FIN
    if INICIO in texto and FIN in texto:
        texto = re.sub(re.escape(INICIO) + r".*?" + re.escape(FIN), lambda m: bloque, texto, flags=re.S)
    else:
        texto = texto.rstrip() + "\n## Diagrama del plano\nEl dibujo se genera desde las tablas de nodos y rutas y no se edita a mano.\n" + bloque + "\n"
    nota.write_text(texto, encoding="utf-8")
    cuenta, espera_total, n_demoras = resumen(nodos, juego)
    print("generar-diagrama: %d nodos, %d rutas, %d hojas | retrabajos %d | esperas %d (%s) | traslapes 0 | cruces 0" % (
        len(nodos), len(rutas), len(hojas), sum(1 for r in rutas if r["tipo"] == "retrabajo"), n_demoras, bonito(espera_total)))
    if "--html" in args:
        salida = pathlib.Path(args[args.index("--html") + 1])
        salida.write_text(entregable(nodos, rutas, meta, juego, figura, rango, hojas, alto_total), encoding="utf-8")
        print("generar-diagrama: entregable escrito en", salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
