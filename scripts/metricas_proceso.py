#!/usr/bin/env python3
"""Métricas de proceso y de proyecto desde GitHub, para los tres repos.

* Proceso: lead time de cada PR (apertura → merge), proporción de PRs de
  corrección (`fix`) que traen un test, duración del último run verde del CI.
* Proyecto: PRs mergeados por semana (throughput) en las últimas ocho semanas.

Escribe ``mediciones/proceso-<fecha>.json`` y ``.md``. Usa ``gh`` autenticado.

    python scripts/metricas_proceso.py
"""
from __future__ import annotations

import json
import statistics
import subprocess
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

HUB = Path(__file__).resolve().parent.parent
REPOS = ["OnTimeAI-Backend", "OnTimeAI-Scrapper", "OnTimeAI-Frontend"]
DUENO = "santiago6124"


def gh(args: list[str]) -> list | dict:
    out = subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout
    return json.loads(out) if out.strip() else []


def prs_mergeados(repo: str, limite: int = 200) -> list[dict]:
    return gh(["pr", "list", "--repo", f"{DUENO}/{repo}", "--state", "merged", "--limit", str(limite),
               "--json", "number,title,createdAt,mergedAt,files"])


def duracion_ci(repo: str) -> float | None:
    runs = gh(["run", "list", "--repo", f"{DUENO}/{repo}", "--workflow", "ci.yml", "--branch", "main",
               "--status", "success", "--limit", "5", "--json", "createdAt,updatedAt"])
    duraciones = []
    for r in runs:
        a = datetime.fromisoformat(r["createdAt"].replace("Z", "+00:00"))
        b = datetime.fromisoformat(r["updatedAt"].replace("Z", "+00:00"))
        duraciones.append((b - a).total_seconds() / 60)
    return round(statistics.median(duraciones), 1) if duraciones else None


def medir(repo: str) -> dict:
    prs = prs_mergeados(repo)
    lead = []
    fixes = 0; fixes_con_test = 0
    por_semana: Counter = Counter()
    hoy = datetime.now(timezone.utc)
    for pr in prs:
        c = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
        m = datetime.fromisoformat(pr["mergedAt"].replace("Z", "+00:00"))
        lead.append((m - c).total_seconds() / 3600)
        if pr["title"].lower().startswith("fix"):
            fixes += 1
            if any("test" in f["path"] for f in pr.get("files", [])):
                fixes_con_test += 1
        semanas_atras = (hoy - m).days // 7
        if semanas_atras < 8:
            por_semana[semanas_atras] += 1
    return {
        "prs_mergeados": len(prs),
        "lead_time_h_mediana": round(statistics.median(lead), 1) if lead else None,
        "lead_time_h_p90": round(sorted(lead)[int(len(lead) * 0.9) - 1], 1) if len(lead) >= 10 else None,
        "fixes": fixes,
        "fixes_con_test": fixes_con_test,
        "fixes_con_test_pct": round(fixes_con_test / fixes * 100, 1) if fixes else None,
        "ci_min_mediana": duracion_ci(repo),
        "prs_por_semana_ultimas_8": [por_semana.get(i, 0) for i in range(7, -1, -1)],
    }


def main() -> int:
    res = {"fecha": date.today().isoformat(), "repos": {r: medir(r) for r in REPOS}}
    out = HUB / "mediciones" / f"proceso-{res['fecha']}"
    out.with_suffix(".json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n")
    L = [f"# Métricas de proceso y de proyecto al {res['fecha']}", "",
         "| Repo | PRs mergeados | Lead time mediana (h) | Lead time p90 (h) | Fixes | Fixes con test | CI mediana (min) | PRs/semana (8 semanas, de la más vieja a la actual) |",
         "|---|---|---|---|---|---|---|---|"]
    for r, m in res["repos"].items():
        L.append(f"| {r} | {m['prs_mergeados']} | {m['lead_time_h_mediana']} | {m['lead_time_h_p90']} | {m['fixes']} | "
                 f"{m['fixes_con_test']} ({m['fixes_con_test_pct']} %) | {m['ci_min_mediana']} | {' '.join(str(x) for x in m['prs_por_semana_ultimas_8'])} |")
    L += ["", "Lead time = horas entre la apertura del PR y su merge. Fixes = PRs cuyo título empieza con `fix`; "
          "con test = el PR toca al menos un archivo de tests. CI = mediana de los últimos cinco runs verdes de `ci.yml` en `main`.", ""]
    out.with_suffix(".md").write_text("\n".join(L))
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
