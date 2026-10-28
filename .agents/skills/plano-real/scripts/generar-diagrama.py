#!/usr/bin/env python3
"""Genera el diagrama del plano real desde el expediente.
La fuente son dos tablas: Nodos y Rutas. El acomodo lo hace ELK (Eclipse Layout Kernel),
el mismo motor de los diagramas profesionales de nodos y aristas: reparte las capas, abre
los caminos de cada decision, junta los que se reincorporan y rutea cada linea esquivando
las formas. Si no hay motor disponible, cae al acomodo interno, que es mas apretado.

Si la nota todavia trae la tabla vieja de pasos, se sintetiza un grafo lineal con sus rutas
de excepcion, para no romper expedientes anteriores.

Uso:
  python3 generar-diagrama.py 04_plano-real.md                      escribe el bloque Mermaid en la nota
  python3 generar-diagrama.py 04_plano-real.md --html salida.html   emite ademas el entregable
  python3 generar-diagrama.py 04_plano-real.md --check              sale 1 si el diagrama de la nota quedo viejo
  python3 generar-diagrama.py 04_plano-real.md --diagnostico        reporta cruces, traslapes y resumen
  --set iso5807 | cursograma      juego de simbolos
  --por-hoja N                    altura maxima de cada hoja
"""
import html
import json
import pathlib
import re
import subprocess
import sys

INICIO, FIN = "<!-- diagrama:inicio -->", "<!-- diagrama:fin -->"
SOLIDA = {"observado", "medido"}
LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIR_ELK = pathlib.Path(__file__).resolve().parent / "layout-elk.js"

# forma: (alto base, ancho minimo, factor del texto, caracteres por linea)
# El rombo necesita mas ancho porque su texto solo cabe en la banda del centro, y menos alto
# aparente porque se angosta: de ahi su factor y su ancho minimo.
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
OPCIONES_ELK = {
    "elk.algorithm": "layered",
    "elk.direction": "DOWN",
    "elk.edgeRouting": "ORTHOGONAL",
    "elk.spacing.nodeNode": "58",
    "elk.layered.spacing.nodeNodeBetweenLayers": "74",
    "elk.layered.spacing.edgeNodeBetweenLayers": "26",
    "elk.layered.spacing.edgeEdgeBetweenLayers": "18",
    "elk.layered.nodePlacement.strategy": "NETWORK_SIMPLEX",
    "elk.layered.nodePlacement.favorStraightEdges": "true",
    "elk.layered.crossingMinimization.strategy": "LAYER_SWEEP",
    "elk.layered.cycleBreaking.strategy": "GREEDY",
    "elk.layered.considerModelOrder.strategy": "NODES_AND_EDGES",
    "elk.layered.thoroughness": "20",
    "elk.edgeLabels.placement": "CENTER",
    "elk.padding": "[top=36,left=36,bottom=36,right=36]",
}


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
            if "hacia" in encabezado:
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
    # Solo la etiqueta inicial declara evidencia; una palabra en la cita no la promueve.
    marca = re.match(r"\s*\[(dicho|observado|medido)\]", c or "", re.I)
    return marca.group(1).lower() if marca else "sin observar"


def resolver_forma(fila, juego):
    f = (fila.get("forma") or "").strip().lower()
    if f in FORMAS:
        return f
    if (fila.get("tipo") or "").lower().startswith("decid"):
        return "decision"
    return "operacion" if juego == "cursograma" else "actividad"


def etiqueta_nodo(n, i):
    """Titulo con el numero del paso adelante, igual en la medicion y en el dibujo."""
    num = re.match(r"n?(\d+)$", i or n["id"])
    return ("%s · %s" % (num.group(1), n["texto"])) if num else n["texto"]


def renglon_chico(n):
    """Quien, en que sistema y cuanto espero. Es el renglon que va abajo, en gris."""
    pie = " · ".join(v for v in [(n["quien"] or "").strip(), (n["sistema"] or "").strip()] if v)
    espera = minutos(n["espera"])
    return (("espera %s · " % bonito(espera)) + pie) if espera > 0 else pie


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


def medir(texto, forma, pie=""):
    """Mide la forma con todo el texto y reserva alto para cada renglón.

    Antes solo se ajustaba el ancho. El alto se quedaba fijo, así que el tercer renglón
    del título podía ocupar el mismo espacio que el renglón gris de metadatos.
    """
    alto_base, minimo, factor, chars = FORMAS.get(forma, FORMAS["actividad"])
    lineas = wrap(texto, chars)
    ancho = max(len(l) for l in lineas) * ANCHO_CHAR * factor + 44
    ancho = max(ancho, minimo)
    if pie:
        if forma == "decision":
            dy = 17.0
            holgura = max(0.25, 1 - dy / (alto_base / 2))
            ancho = max(ancho, (len(pie) * 5.6 + 14) / holgura)
        else:
            ancho = max(ancho, len(pie) * 5.6 + 40)
    # Cada línea tiene su propia línea base. Se agrega espacio explícito entre título y meta.
    if forma == "decision":
        alto_necesario = len(lineas) * 15 + (19 if pie else 0) + 24
    else:
        alto_necesario = 22 + len(lineas) * 15 + (18 if pie else 0)
    alto = max(alto_base, alto_necesario)
    return min(ancho, 460), alto, lineas


def posiciones_texto(forma, y, alto, lineas, pie):
    """Devuelve las líneas de título y meta sin coordenadas compartidas ni traslapes."""
    if forma == "decision":
        total = len(lineas) * 15 + (19 if pie else 0)
        inicio = y + alto / 2 - total / 2 + 8
        titulos = [inicio + 15 * k for k in range(len(lineas))]
        meta = inicio + len(lineas) * 15 + 4 if pie else None
        return titulos, meta
    inicio = y + 22
    titulos = [inicio + 15 * k for k in range(len(lineas))]
    meta = inicio + len(lineas) * 15 + 3 if pie else None
    return titulos, meta


# ---------------------------------------------------------------- acomodo con motor

def grafo_motor(nodos, rutas, juego):
    hijos, aristas = [], []
    for n in nodos:
        etiqueta = etiqueta_nodo(n, n["id"])
        ancho, alto, _ = medir(etiqueta, resolver_forma(n["fila"], juego), renglon_chico(n))
        hijos.append({"id": n["id"], "width": round(ancho), "height": round(alto),
                      "labels": [{"text": etiqueta[:40], "width": round(ancho) - 24, "height": 20}]})
    for i, r in enumerate(rutas):
        e = {"id": "e%d" % i, "sources": [r["desde"]], "targets": [r["hacia"]]}
        if r["etiqueta"]:
            e["labels"] = [{"text": r["etiqueta"], "width": round(len(r["etiqueta"]) * 6.4 + 16), "height": 18}]
        aristas.append(e)
    return {"id": "raiz", "layoutOptions": OPCIONES_ELK, "children": hijos, "edges": aristas}


def acomodo_con_motor(nodos, rutas, juego, dir_trabajo):
    """Devuelve (acomodo, motor, aviso). Intenta ELK; si no puede, cae al acomodo interno."""
    aviso = ""
    if DIR_ELK.exists():
        entrada = dir_trabajo / "plano-grafo.json"
        salida = dir_trabajo / "plano-acomodo.json"
        entrada.write_text(json.dumps(grafo_motor(nodos, rutas, juego), ensure_ascii=False), encoding="utf-8")
        for intento in (0, 1):
            r = subprocess.run(["node", str(DIR_ELK), str(entrada), str(salida)], capture_output=True, text=True)
            if r.returncode == 0 and salida.exists():
                return acomodo_desde_motor(json.loads(salida.read_text(encoding="utf-8")), rutas), "elk", ""
            salida_texto = (r.stdout or "") + (r.stderr or "")
            if intento == 0 and "no encontre elkjs" in salida_texto:
                print("generar-diagrama: instalando el motor de acomodo, una sola vez (npm install elkjs)...")
                npm = subprocess.run(["npm", "install", "elkjs", "--no-save", "--silent"],
                                     cwd=str(DIR_ELK.parent), capture_output=True, text=True)
                if npm.returncode == 0:
                    continue
                aviso = "no se pudo instalar elkjs"
            else:
                aviso = salida_texto.strip().splitlines()[-1] if salida_texto.strip() else "el motor fallo"
            break
    else:
        aviso = "falta layout-elk.js"
    return None, "interno", aviso


def acomodo_desde_motor(d, rutas_originales):
    """El motor devuelve las aristas en el mismo orden en que se le dieron, asi que el tipo
    y la etiqueta se recuperan por posicion: sin eso, todas las lineas salen iguales."""
    nodos = {k: (v["x"], v["y"], v["w"], v["h"]) for k, v in d["nodos"].items()}
    rutas = []
    for k, r in enumerate(d["rutas"]):
        original = rutas_originales[k] if k < len(rutas_originales) else {"tipo": "normal", "etiqueta": ""}
        polilineas = [p for p in ([[tuple(pt) for pt in sec] for sec in r["secciones"]]) if len(p) > 1]
        etiqueta_pos = None
        if r.get("etiqueta"):
            e = r["etiqueta"]
            etiqueta_pos = (e["x"] + e["w"] / 2, e["y"] + e["h"] / 2)
        rutas.append({"desde": r["desde"], "hacia": r["hacia"], "tipo": original["tipo"], "etiqueta": original["etiqueta"],
                      "polilineas": polilineas, "etiqueta_pos": etiqueta_pos})
    return {"motor": "elk", "ancho": d["ancho"], "alto": d["alto"], "nodos": nodos, "rutas": rutas}


# ---------------------------------------------------------------- acomodo interno, de respaldo

def capas(nodos, rutas):
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
            if r["desde"] in rango and r["hacia"] in rango and rango[r["hacia"]] < rango[r["desde"]] + 1:
                rango[r["hacia"]] = rango[r["desde"]] + 1
                cambio = True
        if not cambio:
            break
    por_rango, orden = {}, {n["id"]: k for k, n in enumerate(nodos)}
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

    def mediana(i, vecinos):
        v = sorted(pos[j][1] for j in vecinos if j in pos and pos[j][0] != pos[i][0])
        return v[len(v) // 2] if v else pos[i][1]

    for n in range(vueltas):
        orden_k = sorted(por_rango)
        for k in (orden_k if n % 2 == 0 else list(reversed(orden_k))):
            for i in por_rango[k]:
                vecinos = [r["hacia"] for r in salidas[i]] + [r["desde"] for r in entradas[i]]
                pos[i] = (k, mediana(i, vecinos))
            por_rango[k].sort(key=lambda i: pos[i][1])
            for j, i in enumerate(por_rango[k]):
                pos[i] = (k, j)
    return por_rango


def acomodo_interno(nodos, rutas, juego):
    rango, por_rango, salidas, entradas, retorno, inicio = capas(nodos, rutas)
    por_rango = ordenar_filas(por_rango, salidas, entradas)
    figura = {}
    for n in nodos:
        forma = resolver_forma(n["fila"], juego)
        ancho, alto, _ = medir(etiqueta_nodo(n, n["id"]), forma, renglon_chico(n))
        figura[n["id"]] = {"n": n, "forma": forma, "ancho": ancho, "alto": alto}
    alto_fila = {k: max(figura[i]["alto"] for i in fila) for k, fila in por_rango.items()}
    y = MARGEN_Y
    for k in sorted(por_rango):
        for i in por_rango[k]:
            figura[i]["y"] = y + (alto_fila[k] - figura[i]["alto"]) / 2
        y += alto_fila[k] + SEP_Y
    ancho_por_fila = {k: sum(figura[i]["ancho"] for i in fila) + SEP_X * (len(fila) - 1) for k, fila in por_rango.items()}
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
    salida_rutas = []
    for r in rutas:
        pts, lbl, _ = puntos_arista(figura, r, rango, retorno, carril)
        salida_rutas.append({"desde": r["desde"], "hacia": r["hacia"], "tipo": r["tipo"], "etiqueta": r["etiqueta"],
                             "polilineas": [pts], "etiqueta_pos": lbl})
    return {"motor": "interno", "ancho": ancho_total, "alto": y + MARGEN_Y,
            "nodos": {i: (figura[i]["x"], figura[i]["y"], figura[i]["ancho"], figura[i]["alto"]) for i in figura},
            "rutas": salida_rutas}


def puntos_arista(figura, r, rango, retorno, carril):
    s, t = figura[r["desde"]], figura[r["hacia"]]
    mx, my = s["x"] + s["ancho"] / 2, s["y"] + s["alto"]
    retorno_arista = (r["desde"], r["hacia"], r["etiqueta"]) in retorno or rango[r["hacia"]] <= rango[r["desde"]]
    if retorno_arista:
        canal = carril.get((r["desde"], r["hacia"]), MARGEN_X + 600)
        salida_y = s["y"] + s["alto"] + SEP_Y * 0.34
        llegada_y = max(16.0, t["y"] - SEP_Y * 0.34)
        pts = [(mx, s["y"] + s["alto"]), (mx, salida_y), (canal, salida_y), (canal, llegada_y),
               (t["x"] + t["ancho"] / 2 + 16, llegada_y), (t["x"] + t["ancho"] / 2 + 16, t["y"])]
        return pts, (canal + 10, (salida_y + llegada_y) / 2 + 4)
    tx, ty = t["x"] + t["ancho"] / 2, t["y"]
    if abs(mx - tx) < 2:
        return [(mx, my), (tx, ty)], (mx + 8, (my + ty) / 2)
    medio = my + (ty - my) / 2
    return [(mx, my), (mx, medio), (tx, medio), (tx, ty)], ((mx + tx) / 2, medio - 7)


# ---------------------------------------------------------------- hojas y dibujo

def bandas(ac):
    tops = sorted({round(y) for (x, y, w, h) in ac["nodos"].values()})
    grupos = []
    for t in tops:
        if grupos and t - grupos[-1][-1] <= 24:
            grupos[-1].append(t)
        else:
            grupos.append([t])
    salida = []
    for g in grupos:
        cotas = [y + h for (x, y, w, h) in ac["nodos"].values() if round(y) in g]
        salida.append((min(g), max(cotas)))
    return salida


def recorta(puntos, y0, y1):
    partes, actual, cortes = [], [], []
    for k in range(len(puntos) - 1):
        (xa, ya), (xb, yb) = puntos[k], puntos[k + 1]
        da, db = y0 - 0.5 <= ya <= y1 + 0.5, y0 - 0.5 <= yb <= y1 + 0.5
        if da and db:
            if not actual:
                actual = [(xa, ya)]
            actual.append((xb, yb))
        elif da or db:
            borde = y1 if da else y0
            t = (borde - ya) / (yb - ya) if yb != ya else 0
            xc = xa + t * (xb - xa)
            cortes.append((xc, borde))
            if da:
                if not actual:
                    actual = [(xa, ya)]
                actual.append((xc, borde))
                partes.append(actual)
                actual = []
            else:
                if actual:
                    partes.append(actual)
                actual = [(xc, borde), (xb, yb)]
        else:
            if actual:
                partes.append(actual)
                actual = []
    if actual:
        partes.append(actual)
    return [p for p in partes if len(p) > 1], cortes


def armar_hojas(ac, limite):
    alto = ac["alto"]
    bs = bandas(ac)
    if alto <= limite or len(bs) < 2:
        cortes = []
    else:
        cortes = []
        for k in range(len(bs) - 1):
            cortes.append((bs[k][1] + bs[k + 1][0]) / 2)
    paginas, y0, i = [], 0.0, 0
    if not cortes:
        paginas.append({"y0": 0.0, "y1": alto})
    else:
        for corte in cortes:
            paginas.append({"y0": y0, "y1": corte})
            y0 = corte
        paginas.append({"y0": y0, "y1": alto})
    contador = [0]
    for p in paginas:
        p["ids"] = [i for i, (x, y, w, h) in ac["nodos"].items() if p["y0"] - 1 <= y and y + h <= p["y1"] + 1]
        p["rutas"], p["conectores"] = [], []
        p["alto"] = p["y1"] - p["y0"] + 30
        for r in ac["rutas"]:
            partes, marca = [], False
            for poli in r["polilineas"]:
                trozos, cortes_pt = recorta(poli, p["y0"], p["y1"])
                partes += trozos
                for (xc, yc) in cortes_pt:
                    letra = LETRAS[contador[0] % len(LETRAS)]
                    contador[0] += 1
                    loc = yc - p["y0"]
                    p["conectores"].append((xc, loc, letra))
            if partes:
                fin = r["polilineas"][-1][-1]
                marca = p["y0"] - 1 <= fin[1] <= p["y1"] + 1
                lbl = r["etiqueta_pos"]
                if lbl and not (p["y0"] - 1 <= lbl[1] <= p["y1"] + 1):
                    lbl = None
                p["rutas"].append({"desde": r["desde"], "hacia": r["hacia"], "tipo": r["tipo"], "etiqueta": r["etiqueta"],
                                   "partes": partes, "marca": marca, "etiqueta_pos": lbl})
        p["ids"] = [i for i in p["ids"] if i in ac["nodos"]]
    return paginas


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
                 "retrabajo": ("#1D4ED8", ' stroke-dasharray="7 4"'), "rechazo": ("#B91C1C", ' stroke-dasharray="2 3"')}


def dibujar_hoja(ac, pagina, nodos_por_id, juego, con_titulo, con_pie):
    ancho, y0 = ac["ancho"], pagina["y0"]
    partes = ['<svg viewBox="0 0 %g %g" xmlns="http://www.w3.org/2000/svg" class="diagrama">' % (ancho, pagina["alto"]),
              '<defs>' + "".join(
                  '<marker id="flecha%s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>' % (k, c)
                  for k, (c, d) in ESTILO_ARISTA.items()) + '</defs>']
    for r in pagina["rutas"]:
        color, dash = ESTILO_ARISTA.get(r["tipo"], ESTILO_ARISTA["normal"])
        for parte in r["partes"]:
            d = "M" + " L".join("%.1f,%.1f" % (x, y - y0) for x, y in parte)
            marca = ' marker-end="url(#flecha%s)"' % (r["tipo"] if r["tipo"] in ESTILO_ARISTA else "normal") if r["marca"] and parte is r["partes"][-1] else ""
            partes.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"%s%s/>' % (d, color, dash, marca))
        if r["etiqueta"] and r["etiqueta_pos"]:
            lx, ly = r["etiqueta_pos"][0], r["etiqueta_pos"][1] - y0
            ancho_et = len(r["etiqueta"]) * 6.2 + 12
            partes.append('<rect x="%.1f" y="%.1f" width="%.1f" height="16" rx="3" fill="#FFFFFF" stroke="#E5E7EB" stroke-width="1"/>' % (lx - ancho_et / 2, ly - 12, ancho_et))
            partes.append('<text x="%.1f" y="%.1f" class="etiqueta-ruta" text-anchor="middle">%s</text>' % (lx, ly, html.escape(r["etiqueta"])))
    for (cx, cy, letra) in pagina["conectores"]:
        partes.append('<circle cx="%.1f" cy="%.1f" r="17" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>' % (cx, cy))
        partes.append('<text x="%.1f" y="%.1f" class="nodo" text-anchor="middle">%s</text>' % (cx, cy + 5, letra))
    for i in pagina["ids"]:
        n = nodos_por_id[i]
        forma = resolver_forma(n["fila"], juego)
        x, y, w, h = ac["nodos"][i]
        y -= y0
        solida = clase_evidencia(n["evidencia"]) in SOLIDA or forma in ("inicio", "fin")
        partes.append(forma_svg(forma, x, y, w, h, solida))
        etiqueta = etiqueta_nodo(n, i)
        lineas = wrap(etiqueta, FORMAS.get(forma, FORMAS["actividad"])[3])
        pie = renglon_chico(n)
        ys_titulo, y_meta = posiciones_texto(forma, y, h, lineas, pie)
        if forma == "decision":
            partes += ['<text x="%.1f" y="%.1f" class="nodo" text-anchor="middle">%s</text>' % (x + w / 2, yy, html.escape(l))
                       for l, yy in zip(lineas, ys_titulo)]
        elif forma == "conector":
            partes.append('<text x="%.1f" y="%.1f" class="nodo" text-anchor="middle">%s</text>' % (x + w / 2, y + h / 2 + 5, html.escape(lineas[0])))
        else:
            partes += ['<text x="%.1f" y="%.1f" class="nodo">%s</text>' % (x + 16, yy, html.escape(l))
                       for l, yy in zip(lineas, ys_titulo)]
        if pie and y_meta is not None:
            if forma == "decision":
                # El rombo se angosta hacia abajo; el ancho ya fue reservado por medir().
                partes.append('<text x="%.1f" y="%.1f" class="mini" text-anchor="middle">%s</text>' % (x + w / 2, y_meta, html.escape(pie[:40])))
            else:
                partes.append('<text x="%.1f" y="%.1f" class="mini">%s</text>' % (x + 16, y_meta, html.escape(pie[:40])))
    partes.append("</svg>")
    return "\n".join(partes)


def choques(bboxes):
    fallas = []
    for i in range(len(bboxes)):
        for j in range(i + 1, len(bboxes)):
            ax, ay, aw, ah, an = bboxes[i]
            bx, by, bw, bh, bn = bboxes[j]
            if ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah:
                fallas.append((an, bn))
    return fallas


def cruces(ac):
    """Segmentos de ruta que atraviesan una forma que no es su origen ni su destino."""
    fallas, cajas = [], ac["nodos"]
    for r in ac["rutas"]:
        for poli in r["polilineas"]:
            for k in range(len(poli) - 1):
                (x1, y1), (x2, y2) = poli[k], poli[k + 1]
                for nid, (fx, fy, fw, fh) in cajas.items():
                    if nid in (r["desde"], r["hacia"]):
                        continue
                    if abs(x1 - x2) < 0.6:
                        if fx + 2 < x1 < fx + fw - 2 and min(y1, y2) < fy + fh - 2 and fy + 2 < max(y1, y2):
                            fallas.append((r["desde"], r["hacia"], nid))
                    elif abs(y1 - y2) < 0.6:
                        if fy + 2 < y1 < fy + fh - 2 and min(x1, x2) < fx + fw - 2 and fx + 2 < max(x1, x2):
                            fallas.append((r["desde"], r["hacia"], nid))
    return fallas


def problemas_texto(nodos, ac, juego):
    """Detecta el síntoma que el chequeo anterior no veía: líneas de texto encimadas."""
    fallas = []
    for n in nodos:
        i = n["id"]
        if i not in ac["nodos"]:
            continue
        forma = resolver_forma(n["fila"], juego)
        x, y, w, h = ac["nodos"][i]
        lineas = wrap(etiqueta_nodo(n, i), FORMAS.get(forma, FORMAS["actividad"])[3])
        pie = renglon_chico(n)
        ys, y_meta = posiciones_texto(forma, y, h, lineas, pie)
        for a, b in zip(ys, ys[1:]):
            if b - a < 12:
                fallas.append((i, "lineas del titulo", round(a), round(b)))
        if y_meta is not None and ys and y_meta - ys[-1] < 10:
            fallas.append((i, "titulo contra metadatos", round(ys[-1]), round(y_meta)))
        for yy in ys + ([y_meta] if y_meta is not None else []):
            if yy < y + 6 or yy > y + h - 4:
                fallas.append((i, "texto cerca del borde", round(yy), round(y), round(h)))
    return fallas


def problemas_etiquetas(ac):
    """Detecta etiquetas de rutas encimadas entre si o sobre una forma ajena."""
    etiquetas = []
    for r in ac["rutas"]:
        if not r.get("etiqueta") or not r.get("etiqueta_pos"):
            continue
        x, y = r["etiqueta_pos"]
        etiquetas.append((r, {"x": x - (len(r["etiqueta"]) * 6.2 + 12) / 2, "y": y - 12,
                           "w": len(r["etiqueta"]) * 6.2 + 12, "h": 16}))
    fallas = []
    for idx, (r, a) in enumerate(etiquetas):
        for nid, (x, y, w, h) in ac["nodos"].items():
            if nid in (r["desde"], r["hacia"]):
                continue
            if a["x"] < x + w and x < a["x"] + a["w"] and a["y"] < y + h and y < a["y"] + a["h"]:
                fallas.append((r["etiqueta"], "sobre nodo " + nid))
        for r2, b in etiquetas[idx + 1:]:
            if a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]:
                fallas.append((r["etiqueta"], "sobre etiqueta " + r2["etiqueta"]))
    return fallas


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


def ficha_html(meta):
    campos = [("entradas", "a", "Entradas requeridas"), ("salidas", "a", "Salidas esperadas"),
              ("secuencia", "b", "Secuencia e interacción"), ("criterios", "c", "Criterios y métodos"),
              ("recursos", "d", "Recursos necesarios"), ("responsables", "e", "Responsabilidades y autoridades"),
              ("riesgos", "g", "Riesgos y oportunidades"), ("mejora", "h", "Evaluación y mejora")]
    filas = "".join("<tr><td><b>%s</b> (%s)</td><td>%s</td></tr>" % (nombre, letra, html.escape(meta[clave]))
                    for clave, letra, nombre in campos if meta.get(clave))
    return ('<h2>Ficha del proceso</h2><table><tr><th>Requisito de ISO 9001:2015, 4.4.1</th><th>Cómo se cumple aquí</th></tr>%s</table>' % filas) if filas else ""


CAMBIO = (".hoja + .hoja{break-before:page;page-break-before:always;}\n"
          "@page retrato{size:letter portrait;margin:0;}\n"
          "@page apaisado{size:letter landscape;margin:0;}\n"
          ".hoja-apaisada{page:apaisado;}\n")

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
    ".hoja h3{font-family:'Montserrat',sans-serif;font-size:9.5pt;font-weight:600;color:#4B5563;text-transform:uppercase;letter-spacing:.6pt;margin-bottom:2pt;}\n"
    ".diagrama{width:100%;height:auto;display:block;}\n"
    ".nodo{font-family:'Inter',sans-serif;font-size:13px;font-weight:600;fill:#1A1A1A;}\n"
    ".mini{font-family:'Inter',sans-serif;font-size:10px;fill:#6B7280;}\n"
    ".etiqueta-ruta{font-family:'Inter',sans-serif;font-size:10.5px;font-weight:600;fill:#374151;}\n"
    "table{width:100%;border-collapse:collapse;font-size:9pt;}\n"
    "th,td{border:1pt solid var(--line);padding:4pt 6pt;text-align:left;vertical-align:top;}\n"
    "th{background:#F3F4F6;font-weight:600;}\n"
    ".leyenda{display:flex;gap:14pt;font-size:8.5pt;color:#374151;margin:6pt 0 4pt;flex-wrap:wrap;}\n"
    ".sw{display:inline-block;width:22pt;height:0;border-top:2pt solid #1A1A1A;vertical-align:middle;margin-right:3pt;}\n"
    ".sw.exc{border-top-style:dashed;border-color:#C2410C;}\n"
    ".sw.ret{border-top-style:dashed;border-color:#1D4ED8;}\n"
    ".sw.rech{border-top-style:dotted;border-color:#B91C1C;}\n"
    ".pie{margin-top:14pt;border-top:1pt solid var(--line);padding-top:6pt;font-size:8pt;color:#4B5563;}\n"
    "@media print{body{width:100%;padding:26pt;} .hoja .diagrama{max-height:172mm;width:auto;max-width:100%;margin:0 auto;}}\n"
    "@page{size:letter portrait;margin:0;}\n") + CAMBIO + (
    "@media screen{body{width:auto;max-width:100%;padding:22pt 20pt;} .hoja + .hoja{break-before:auto;page-break-before:auto;}}\n")


def entregable(nodos, rutas, meta, juego, hojas, ac):
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
    motor = "ELK" if ac["motor"] == "elk" else "acomodo interno"
    cuerpo = "".join('<div class="hoja hoja-apaisada"><h3>Cómo camina el trabajo%s</h3>%s</div>'
                     % ("" if len(hojas) == 1 else ", hoja %d de %d" % (i + 1, len(hojas)), s) for i, s in enumerate(hojas))
    return "\n".join([
        "<!DOCTYPE html>", '<html lang="es-MX"><head><meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        "<title>Plano real: %s</title>" % html.escape(meta.get("proceso", "")),
        "<style>%s</style></head><body>" % CSS,
        "<h1>El plano real de la operación</h1>",
        '<div class="sub">%s · Proceso: %s · %s · Simbología: %s · Acomodo: %s</div>' % (html.escape(meta.get("cliente", "")), html.escape(meta.get("proceso", "")), html.escape(meta.get("fase", "")), simb, motor),
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
        '<div class="pie">Generado desde las tablas de nodos y rutas del expediente, con los símbolos de %s y el acomodo de %s. El diagrama no se edita a mano: si las tablas cambian, se vuelve a generar. Cada rombo declara su condición en la ruta que sale de él. Los nodos en gris punteado están sin observar y no sostienen un rediseño todavía. Nodos sin observar: %d.</div>' % (simb, motor, sinobs),
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
    if juego not in ("iso5807", "cursograma"):
        print("generar-diagrama: el juego de simbolos debe ser iso5807 o cursograma")
        return 2
    limite = int(args[args.index("--por-hoja") + 1]) if "--por-hoja" in args else 1500
    texto = nota.read_text(encoding="utf-8")
    meta, tablas = leer_secciones(texto)
    nodos, rutas = grafo(meta, tablas)
    if not nodos:
        print("generar-diagrama: no encontre nodos ni tabla de pasos en", nota)
        return 1
    dir_trabajo = nota.parent if nota.parent.is_dir() else pathlib.Path(".")
    ac, motor, aviso = acomodo_con_motor(nodos, rutas, juego, dir_trabajo)
    if ac is None:
        ac = acomodo_interno(nodos, rutas, juego)
        print("generar-diagrama: sin motor de acomodo (%s), use el acomodo interno." % (aviso or "no disponible"))
        print("generar-diagrama: para el acomodo bueno, corre npm install elkjs junto a este script.")
    nodos_por_id = {n["id"]: n for n in nodos}
    desconocidas = sorted({(n["fila"].get("forma") or "").lower() for n in nodos if (n["fila"].get("forma") or "").lower() and (n["fila"].get("forma") or "").lower() not in FORMAS})
    paginas = armar_hojas(ac, limite)
    hojas = [dibujar_hoja(ac, p, nodos_por_id, juego, i == 0, i == len(paginas) - 1) for i, p in enumerate(paginas)]
    bboxes = [(ac["nodos"][i][0], ac["nodos"][i][1] - p["y0"], ac["nodos"][i][2], ac["nodos"][i][3], resolver_forma(nodos_por_id[i]["fila"], juego))
              for p in paginas for i in p["ids"]]
    choques_totales = choques([b for b in bboxes])
    cruces_totales = cruces(ac)
    texto_fallas = problemas_texto(nodos, ac, juego)
    etiqueta_fallas = problemas_etiquetas(ac)
    der = mermaid(nodos, rutas, juego)
    if "--diagnostico" in args:
        cuenta, espera_total, n_demoras = resumen(nodos, juego)
        salidas_n = {}
        for r in rutas:
            salidas_n[r["desde"]] = salidas_n.get(r["desde"], 0) + 1
        decisiones = [n["id"] for n in nodos if resolver_forma(n["fila"], juego) == "decision"]
        print("motor de acomodo:", motor, ("| aviso: " + aviso) if aviso else "")
        print("nodos: %d | rutas: %d | hojas: %d" % (len(nodos), len(rutas), len(hojas)))
        print("lienzo: %.0f x %.0f | aspecto %.2f" % (ac["ancho"], ac["alto"], ac["alto"] / ac["ancho"]))
        print("formas:", dict((k, v[0]) for k, v in sorted(cuenta.items())))
        print("decisiones: %d, con dos o mas salidas: %d" % (len(decisiones), sum(1 for d in decisiones if salidas_n.get(d, 0) >= 2)))
        print("rutas de retrabajo:", sum(1 for r in rutas if r["tipo"] == "retrabajo"), "| de excepcion:", sum(1 for r in rutas if r["tipo"] == "excepcion"), "| de rechazo:", sum(1 for r in rutas if r["tipo"] == "rechazo"))
        print("esperas: %d, total %s" % (n_demoras, bonito(espera_total)))
        print("traslapes:", choques_totales if choques_totales else "ninguno")
        print("rutas que atraviesan una forma:", sorted(set(cruces_totales)) if cruces_totales else "ninguna")
        print("texto encimado o cerca del borde:", texto_fallas if texto_fallas else "ninguno")
        print("etiquetas encimadas:", etiqueta_fallas if etiqueta_fallas else "ninguna")
        print("formas desconocidas:", desconocidas if desconocidas else "ninguna")
        return 1 if (choques_totales or cruces_totales or texto_fallas or etiqueta_fallas or desconocidas) else 0
    if desconocidas:
        print("generar-diagrama: formas que no existen en el juego %s: %s" % (juego, ", ".join(desconocidas)))
        return 1
    if choques_totales:
        print("generar-diagrama: el acomodo produce %d traslapes: %s" % (len(choques_totales), choques_totales[:3]))
        return 1
    if cruces_totales:
        print("generar-diagrama: hay %d rutas que atraviesan una forma: %s" % (len(cruces_totales), sorted(set(cruces_totales))[:3]))
        return 1
    if texto_fallas:
        print("generar-diagrama: hay texto encimado o cerca del borde: %s" % texto_fallas[:5])
        return 1
    if etiqueta_fallas:
        print("generar-diagrama: hay etiquetas encimadas: %s" % etiqueta_fallas[:5])
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
    print("generar-diagrama: %d nodos, %d rutas, %d hojas, acomodo %s | retrabajos %d | esperas %d (%s) | traslapes %d | cruces %d" % (
        len(nodos), len(rutas), len(hojas), motor, sum(1 for r in rutas if r["tipo"] == "retrabajo"), n_demoras, bonito(espera_total),
        len(choques_totales), len(cruces_totales)))
    if "--html" in args:
        salida = pathlib.Path(args[args.index("--html") + 1])
        salida.write_text(entregable(nodos, rutas, meta, juego, hojas, ac), encoding="utf-8")
        print("generar-diagrama: entregable escrito en", salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
