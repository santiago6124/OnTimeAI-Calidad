#!/usr/bin/env python3
"""Resume una carpeta de mediciones (raw/) en resumen.json y resumen.md.

Lee lo que haya en ``<carpeta>/raw/``:

* ``cobertura-<repo>.xml``   (Cobertura XML de pytest-cov, con ramas)
* ``cobertura-frontend.json`` (coverage-summary.json de vitest/v8)
* ``cc-ruff-<repo>.json``    (salida JSON de ``ruff check --select C901``)
* ``cc-radon-<repo>.json``   (salida JSON de ``radon cc -j``)
* ``cc-eslint-frontend.json`` (salida JSON de eslint con la regla complexity a 0)
* ``tests-<repo>.json``      (conteo de tests, opcional)

y escribe un resumen comparable entre fechas. Uso::

    python scripts/resumir.py mediciones/2026-10-22-antes
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from statistics import mean

REPOS = ("backend", "scrapper", "frontend")
UMBRAL = 10


def cobertura_xml(p: Path) -> dict:
    raiz = ET.parse(p).getroot()
    lineas = int(raiz.get("lines-valid", 0)); cubiertas = int(raiz.get("lines-covered", 0))
    ramas = int(raiz.get("branches-valid", 0)); ramas_cub = int(raiz.get("branches-covered", 0))
    archivos = {}
    for cls in raiz.iter("class"):
        archivos[cls.get("filename")] = round(float(cls.get("line-rate", 0)) * 100, 1)
    return {
        "lineas_pct": round(cubiertas / lineas * 100, 1) if lineas else 0.0,
        "lineas": lineas, "lineas_cubiertas": cubiertas,
        "ramas_pct": round(ramas_cub / ramas * 100, 1) if ramas else 0.0,
        "ramas": ramas, "ramas_cubiertas": ramas_cub,
        "por_archivo": archivos,
    }


def cobertura_vitest(p: Path) -> dict:
    d = json.loads(p.read_text()); t = d["total"]
    por_archivo = {k.split("/src/")[-1]: v["lines"]["pct"] for k, v in d.items() if k != "total"}
    return {
        "lineas_pct": t["lines"]["pct"], "lineas": t["lines"]["total"], "lineas_cubiertas": t["lines"]["covered"],
        "ramas_pct": t["branches"]["pct"], "ramas": t["branches"]["total"], "ramas_cubiertas": t["branches"]["covered"],
        "funciones_pct": t["functions"]["pct"],
        "por_archivo": por_archivo,
    }


_RUFF = re.compile(r"`(?P<n>[^`]+)` is too complex \((?P<cc>\d+) > \d+\)")


def cc_ruff(p: Path) -> dict:
    items = json.loads(p.read_text())
    funcs = {}
    for it in items:
        m = _RUFF.search(it["message"])
        if m:
            rel = it["filename"]
            rel = rel.split("/", 1)[1] if rel.startswith("/") and "/" in rel else rel
            funcs[f"{Path(it['filename']).name}::{m['n']}"] = {"cc": int(m["cc"]), "archivo": it["filename"], "linea": it["location"]["row"]}
    return {"sobre_umbral": len(funcs), "funciones": dict(sorted(funcs.items(), key=lambda kv: -kv[1]["cc"]))}


def cc_radon(p: Path) -> dict:
    d = json.loads(p.read_text()); vals = []; top = []
    for archivo, bloques in d.items():
        if isinstance(bloques, dict):
            continue
        for b in bloques:
            vals.append(b["complexity"]); top.append((b["complexity"], archivo, b["name"], b["lineno"]))
    top.sort(reverse=True)
    return {
        "bloques": len(vals), "promedio": round(mean(vals), 2) if vals else 0,
        "sobre_10": sum(v > 10 for v in vals), "sobre_15": sum(v > 15 for v in vals),
        "sobre_20": sum(v > 20 for v in vals), "sobre_30": sum(v > 30 for v in vals),
        "top": [{"cc": c, "archivo": a, "nombre": n, "linea": l} for c, a, n, l in top[:15]],
    }


_ESL = re.compile(r"complexity of (\d+)")


def cc_eslint(p: Path) -> dict:
    d = json.loads(p.read_text()); vals = []; top = []
    for f in d:
        for m in f.get("messages", []):
            if m.get("ruleId") != "complexity":
                continue
            cc = int(_ESL.search(m["message"]).group(1))
            nombre = m["message"].split(" has a complexity")[0]
            vals.append(cc); top.append((cc, f["filePath"].split("/src/")[-1], nombre, m["line"]))
    top.sort(reverse=True)
    return {
        "funciones": len(vals), "promedio": round(mean(vals), 2) if vals else 0,
        "sobre_10": sum(v > 10 for v in vals), "sobre_15": sum(v > 15 for v in vals),
        "sobre_20": sum(v > 20 for v in vals),
        "top": [{"cc": c, "archivo": a, "nombre": n, "linea": l} for c, a, n, l in top[:15]],
    }


def resumir(carpeta: Path) -> dict:
    raw = carpeta / "raw"; out: dict = {"carpeta": carpeta.name, "repos": {}}
    for repo in REPOS:
        r: dict = {}
        if (raw / f"cobertura-{repo}.xml").exists():
            r["cobertura"] = cobertura_xml(raw / f"cobertura-{repo}.xml")
        elif (raw / f"cobertura-{repo}.json").exists():
            r["cobertura"] = cobertura_vitest(raw / f"cobertura-{repo}.json")
        if (raw / f"cc-ruff-{repo}.json").exists():
            r["cc_ruff"] = cc_ruff(raw / f"cc-ruff-{repo}.json")
        if (raw / f"cc-radon-{repo}.json").exists():
            r["cc_radon"] = cc_radon(raw / f"cc-radon-{repo}.json")
        if (raw / f"cc-eslint-{repo}.json").exists():
            r["cc_eslint"] = cc_eslint(raw / f"cc-eslint-{repo}.json")
        if (raw / f"tests-{repo}.json").exists():
            r["tests"] = json.loads((raw / f"tests-{repo}.json").read_text())
        if (raw / f"meta-{repo}.json").exists():
            r["meta"] = json.loads((raw / f"meta-{repo}.json").read_text())
        if r:
            out["repos"][repo] = r
    return out


def markdown(res: dict) -> str:
    L = [f"# Medición `{res['carpeta']}`", ""]
    L += ["| Repo | Commit | Tests | Cobertura líneas | Cobertura ramas | Funciones > 10 (gate) | Promedio CC (radon) | > 20 (radon) |",
          "|---|---|---|---|---|---|---|---|"]
    for repo, r in res["repos"].items():
        cob = r.get("cobertura", {}); meta = r.get("meta", {}); t = r.get("tests", {})
        gate = r.get("cc_ruff", {}).get("sobre_umbral", r.get("cc_eslint", {}).get("sobre_10", "—"))
        radon = r.get("cc_radon", {})
        prom = radon.get("promedio", r.get("cc_eslint", {}).get("promedio", "—"))
        s20 = radon.get("sobre_20", r.get("cc_eslint", {}).get("sobre_20", "—"))
        L.append(f"| {repo} | `{meta.get('commit', '—')}` | {t.get('total', '—')} | {cob.get('lineas_pct', '—')} % ({cob.get('lineas_cubiertas', '—')}/{cob.get('lineas', '—')}) | {cob.get('ramas_pct', '—')} % | {gate} | {prom} | {s20} |")
    for repo, r in res["repos"].items():
        top = r.get("cc_radon", r.get("cc_eslint", {})).get("top", [])[:10]
        if not top:
            continue
        L += ["", f"## {repo}: funciones más complejas", "", "| CC | Función | Archivo |", "|---|---|---|"]
        for t in top:
            L.append(f"| {t['cc']} | `{t['nombre']}` | `{t['archivo']}:{t['linea']}` |")
    L.append("")
    return "\n".join(L)


def main(argv: list[str]) -> int:
    carpeta = Path(argv[1]) if len(argv) > 1 else None
    if not carpeta or not (carpeta / "raw").is_dir():
        print(__doc__); return 2
    res = resumir(carpeta)
    (carpeta / "resumen.json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n")
    (carpeta / "resumen.md").write_text(markdown(res))
    print(f"resumen escrito en {carpeta}/resumen.{{json,md}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
