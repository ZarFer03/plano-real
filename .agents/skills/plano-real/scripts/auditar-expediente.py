#!/usr/bin/env python3
"""Compuerta de archivo del expediente de operaciones.
Uso: python3 auditar-expediente.py <ruta del expediente> [--fase N]
Sale con codigo 1 si hay fallas. Solo libreria estandar."""
import pathlib, re, sys, collections

REQUERIDOS = {
    0: ["00_AGENT_BRIEF.md", "01_alcance.md"],
    1: ["00_AGENT_BRIEF.md", "01_alcance.md", "02_quien-es-quien.md"],
    2: ["00_AGENT_BRIEF.md", "01_alcance.md", "02_quien-es-quien.md", "04_plano-real.md"],
    3: ["04_plano-real.md", "05_linea-base.md", "06_prioridad.md"],
    4: ["07_rediseno.md", "08_prueba.md"],
    5: ["09_custodia.md"],
}
ENTREGABLES = {"04_plano-real.md", "05_linea-base.md", "06_prioridad.md", "07_rediseno.md", "08_prueba.md", "09_custodia.md"}
CLASES = ["dicho", "observado", "medido", "firmado"]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("Uso: python3 auditar-expediente.py <ruta del expediente> [--fase N]")
        return 2
    raiz = pathlib.Path(args[0]).expanduser().resolve()
    fase = None
    if "--fase" in sys.argv:
        try:
            fase = int(sys.argv[sys.argv.index("--fase") + 1])
        except (IndexError, ValueError):
            print("auditar-expediente: --fase necesita un numero de 0 a 5")
            return 2
    if not raiz.is_dir():
        print("auditar-expediente: no existe el expediente", raiz)
        return 2

    notas = sorted(p for p in raiz.rglob("*.md"))
    if not notas:
        print("auditar-expediente: el expediente no tiene notas markdown:", raiz)
        return 1

    fallas = collections.defaultdict(list)
    avisos = collections.defaultdict(list)
    conteo = {c: 0 for c in CLASES}

    # 1) archivos requeridos por fase
    if fase is not None and fase in REQUERIDOS:
        for req in REQUERIDOS[fase]:
            if not (raiz / req).exists():
                fallas["archivo_faltante"].append(f"{req} (fase {fase})")
    if (raiz / "03_entrevistas").is_dir() and not list((raiz / "03_entrevistas").glob("*.md")):
        fallas["entrevistas_vacias"].append("03_entrevistas/ no tiene ninguna nota")

    # 2) enlaces rotos, lineas en blanco y guiones largos
    for p in notas:
        t = p.read_text(encoding="utf-8")
        rel = str(p.relative_to(raiz))
        for destino in re.findall(r"\]\(([^)]+)\)", t):
            if destino.startswith(("http", "#", "mailto:")):
                continue
            if not (p.parent / destino.split("#")[0]).exists():
                fallas["enlace_roto"].append(f"{rel} -> {destino}")
        dentro = False
        for i, linea in enumerate(t.split("\n")[:-1], 1):
            if linea.strip().startswith("```"):
                dentro = not dentro
                continue
            if not dentro and linea.strip() == "":
                fallas["linea_en_blanco"].append(f"{rel}:{i}")
            if "\u2014" in linea or "\u2013" in linea:
                fallas["guion_largo"].append(f"{rel}:{i}")
        # 3) clases de evidencia, y dicho sin recibo
        for c in CLASES:
            encontrados = t.count(f"[{c}]")
            conteo[c] += encontrados
            if c == "dicho":
                for linea in t.split("\n"):
                    if "[dicho]" in linea and "(" not in linea:
                        fallas["dicho_sin_recibo"].append(f"{rel}: {linea.strip()[:80]}")
        # 4) entregable sin evidencia observada ni medida
        if p.name in ENTREGABLES and not (t.count("[observado]") or t.count("[medido]")):
            fallas["entregable_sin_evidencia"].append(f"{rel} no cita ninguna observacion ni medicion")
        # 5) datos faltantes declarados
        for m in re.finditer(r"\[FALTA DATO[^\]]*\]", t):
            avisos["falta_dato"].append(f"{rel}: {m.group(0)[:90]}")

    # 6) brief desactualizado
    brief = raiz / "00_AGENT_BRIEF.md"
    if brief.exists():
        mas_nuevo = max((p.stat().st_mtime for p in notas if p.name != "00_AGENT_BRIEF.md"), default=0)
        if mas_nuevo > brief.stat().st_mtime:
            avisos["brief_desactualizado"].append("hay notas mas nuevas que 00_AGENT_BRIEF.md")

    print(f"Expediente: {raiz}")
    print(f"Notas: {len(notas)} | fase auditada: {fase if fase is not None else 'sin declarar'}")
    print("Evidencia:", {k: v for k, v in conteo.items()})
    if not any(conteo.values()):
        avisos["sin_evidencia"].append("el expediente no tiene ninguna clase de evidencia marcada")
    total = sum(len(v) for v in fallas.values())
    print("Fallas:", total)
    for k in sorted(fallas):
        for v in fallas[k]:
            print(f"  {k}: {v}")
    print("Avisos:", sum(len(v) for v in avisos.values()))
    for k in sorted(avisos):
        for v in avisos[k]:
            print(f"  {k}: {v}")
    print("EXPEDIENTE OK" if total == 0 else "EXPEDIENTE CON FALLAS")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
