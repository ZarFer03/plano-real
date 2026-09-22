#!/usr/bin/env python3
"""Compuerta de archivo del expediente de operaciones.
Uso: python3 auditar-expediente.py <ruta del expediente> --fase N
Sale con codigo 1 si hay fallas. Solo libreria estandar."""
import pathlib, re, subprocess, sys, collections

REQUERIDOS = {
    0: ["00_AGENT_BRIEF.md", "01_alcance.md"],
    1: ["00_AGENT_BRIEF.md", "01_alcance.md", "02_quien-es-quien.md"],
    2: ["00_AGENT_BRIEF.md", "01_alcance.md", "02_quien-es-quien.md", "04_plano-real.md"],
    3: ["04_plano-real.md", "05_linea-base.md", "06_prioridad.md"],
    4: ["07_rediseno.md", "08_prueba.md"],
    5: ["09_custodia.md"],
}
ENTREGABLES = {"04_plano-real.md", "05_linea-base.md", "06_prioridad.md", "07_rediseno.md", "08_prueba.md", "09_custodia.md"}
CLASES = ["dicho", "observado", "medido"]


def recibo_valido(clase, texto, documento, raiz):
    """Valida estructura, no veracidad. Fuentes locales relativas al documento."""
    import datetime
    fechas = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", texto)
    if clase != "medido":
        if not fechas:
            return False
        try:
            for fecha in fechas:
                datetime.date.fromisoformat(fecha)
        except ValueError:
            return False
    if clase == "observado":
        return bool(re.search(r"\bcaso\s+[^\s,|]+.*\bcon\s+[^,|]+,?\s+el\s+\d{4}-\d{2}-\d{2}", texto))
    if clase == "firmado":
        return bool(re.search(r"\S.+ revisado por \S.+ el \d{4}-\d{2}-\d{2}", texto))
    if clase == "dicho":
        return bool(re.search(r'["“].+?["”]\s*\([^,()]+,\s*[^,()]+,\s*\d{4}-\d{2}-\d{2},\s*[^,()]+\)', texto))
    fuente = re.search(r"\(fuente:\s*([^()]+)\)", texto)
    if not fuente:
        return False
    if clase == "aprobado":
        if not re.fullmatch(r"\S.* versi[oó]n \S+ aprobado por \S.* el \d{4}-\d{2}-\d{2} \(fuente: [^()]+\)", texto):
            return False
    elif not re.search(r"\S.+ con m[ée]todo \S.+:\s*\S.+?=\s*\S", texto):
        return False
    ruta = (documento.parent / fuente.group(1).strip().strip("`")).resolve()
    return ruta.is_relative_to(raiz) and ruta.is_file()


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expediente")
    parser.add_argument("--fase", type=int, choices=range(6), required=True)
    args = parser.parse_args()
    raiz = pathlib.Path(args.expediente).expanduser().resolve()
    fase = args.fase
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
    requeridos = sorted({req for n in range(fase + 1) for req in REQUERIDOS[n]})
    for req in requeridos:
        if not (raiz / req).is_file():
            fallas["archivo_faltante"].append(f"{req} (hasta fase {fase})")
    if fase >= 1 and not any((raiz / "03_entrevistas").glob("*.md")):
        fallas["entrevistas_vacias"].append("03_entrevistas/ requiere al menos una nota")

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
                avisos["linea_en_blanco"].append(f"{rel}:{i}")
            if "\u2014" in linea or "\u2013" in linea:
                avisos["guion_largo"].append(f"{rel}:{i}")
        # 3) cada etiqueta necesita su propio recibo en la misma celda/linea.
        for i, linea in enumerate(t.splitlines(), 1):
            for celda in linea.split("|"):
                marcas = list(re.finditer(r"\[(dicho|observado|medido|firmado|aprobado)\]", celda))
                for j, marca in enumerate(marcas):
                    c = marca.group(1)
                    if c in conteo:
                        conteo[c] += 1
                    elif c == "firmado":
                        avisos["firma_legacy"].append(f"{rel}:{i}: firma histórica, no evidencia ni autorización vigente; migrar con recibo")
                    fin = marcas[j + 1].start() if j + 1 < len(marcas) else len(celda)
                    recibo = celda[marca.end():fin].strip()
                    if not recibo_valido(c, recibo, p, raiz):
                        fallas["recibo_invalido"].append(f"{rel}:{i}: [{c}] requiere campos completos y fuente local para medido")
        # 4) entregable sin evidencia observada ni medida
        if p.name in ENTREGABLES and not (t.count("[observado]") or t.count("[medido]")):
            fallas["entregable_sin_evidencia"].append(f"{rel} no cita ninguna observacion ni medicion")
        # 5) datos faltantes declarados
        for m in re.finditer(r"\[FALTA DATO[^\]]*\]", t):
            avisos["falta_dato"].append(f"{rel}: {m.group(0)[:90]}")

    # 6) el diagrama del plano no coincide con la tabla de pasos
    gen = pathlib.Path(__file__).parent / "generar-diagrama.py"
    plano = raiz / "04_plano-real.md"
    if gen.exists() and plano.exists() and "<!-- diagrama:inicio -->" in plano.read_text(encoding="utf-8"):
        r = subprocess.run([sys.executable, str(gen), str(plano), "--check"], capture_output=True, text=True)
        if r.returncode != 0:
            fallas["diagrama_vencido"].append("04_plano-real.md: el diagrama quedo viejo, hay que regenerarlo desde la tabla")

    # 7) brief desactualizado
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
