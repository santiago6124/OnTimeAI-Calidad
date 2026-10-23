#!/usr/bin/env python3
"""Mide un repo de OnTimeAI en un commit dado y deja los crudos en mediciones/.

Crea un worktree temporal del repo en ``--ref`` (por defecto ``origin/main``),
corre la suite con cobertura de líneas y ramas, mide complejidad ciclomática
(ruff C901 para el gate, radon para la distribución; ESLint ``complexity`` en el
Frontend) y escribe todo en ``mediciones/<carpeta>/raw/``. Después llama a
``resumir.py``. Nunca toca el checkout de trabajo del repo.

Uso::

    python scripts/medir.py backend  --carpeta 2026-10-22-antes
    python scripts/medir.py scrapper --carpeta 2026-10-22-antes --ref origin/main
    python scripts/medir.py frontend --carpeta 2026-10-22-antes

Requiere los venvs de ``.venvs/`` (ver README) y pnpm para el Frontend.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HUB = Path(__file__).resolve().parent.parent
TESIS = HUB.parent

REPOS = {
    "backend": {
        "ruta": TESIS / "OnTimeAI-Backend",
        "venv": HUB / ".venvs" / "backend",
        # Lo que copian los tres Dockerfiles: es el alcance del gate.
        "productivo": ["api.py", "predict.py", "live_pull.py", "live_job.py", "watchdog.py",
                       "ontimeai", "feature_engineering_v7", "scripts/prune_db.py"],
        # Cobertura: exactamente lo desplegado, igual que `[tool.coverage.run]
        # source` del repo. Sin esto coverage contaría los scripts de análisis,
        # que no se despliegan, y el número no sería el del CI.
        "cov": ["api", "predict", "live_pull", "live_job", "watchdog", "ontimeai",
                "feature_engineering_v7", "scripts.prune_db"],
        "env": {"JWT_SECRET_KEY": "medicion", "API_USERNAME": "medicion", "API_PASSWORD": "medicion",
                "API_USERNAME_VIEWER": "viewer", "API_PASSWORD_VIEWER": "viewer"},
    },
    "scrapper": {
        "ruta": TESIS / "OnTimeAI-Scrapper",
        "venv": HUB / ".venvs" / "scrapper",
        "productivo": ["ontimeai_scrapper"],
        # Lo que copia Dockerfile.harvester; scripts/validate_sources.py es una
        # herramienta de desarrollo y queda fuera.
        "cov": ["ontimeai_scrapper"],
        "env": {},
    },
    "frontend": {
        "ruta": TESIS / "OnTimeAI-Frontend",
    },
}


def sh(cmd: list[str], cwd: Path, env: dict | None = None, check: bool = True) -> subprocess.CompletedProcess:
    e = dict(os.environ); e.update(env or {})
    return subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True, check=check)


def worktree(repo: Path, ref: str, destino: Path) -> str:
    if destino.exists():
        sh(["git", "-C", str(repo), "worktree", "remove", "--force", str(destino)], cwd=HUB, check=False)
        shutil.rmtree(destino, ignore_errors=True)
    sh(["git", "-C", str(repo), "fetch", "-q", "origin"], cwd=HUB, check=False)
    sh(["git", "-C", str(repo), "worktree", "add", "--detach", "-q", str(destino), ref], cwd=HUB)
    return sh(["git", "rev-parse", "--short", "HEAD"], cwd=destino).stdout.strip()


def limpiar(repo: Path, destino: Path) -> None:
    sh(["git", "-C", str(repo), "worktree", "remove", "--force", str(destino)], cwd=HUB, check=False)
    sh(["git", "-C", str(repo), "worktree", "prune"], cwd=HUB, check=False)


def junit(p: Path) -> dict:
    raiz = ET.parse(p).getroot()
    suites = [raiz] if raiz.tag == "testsuite" else list(raiz.iter("testsuite"))
    tot = sum(int(s.get("tests", 0)) for s in suites)
    fall = sum(int(s.get("failures", 0)) + int(s.get("errors", 0)) for s in suites)
    skip = sum(int(s.get("skipped", 0)) for s in suites)
    return {"total": tot, "fallidos": fall, "omitidos": skip, "aprobados": tot - fall - skip}


def medir_python(nombre: str, cfg: dict, wt: Path, raw: Path) -> None:
    py = cfg["venv"] / "bin" / "python"
    covrc = raw / f".coveragerc-{nombre}"
    covrc.write_text("[run]\nbranch = True\nomit =\n    tests/*\n    */site-packages/*\n")
    print(f"[{nombre}] pytest con cobertura…", flush=True)
    r = sh([str(py), "-m", "pytest", "-p", "no:cacheprovider", "-q", "-o", "addopts=",
            *[f"--cov={c}" for c in cfg["cov"]], f"--cov-config={covrc}", "--cov-branch",
            f"--cov-report=xml:{raw / f'cobertura-{nombre}.xml'}",
            f"--junitxml={raw / f'junit-{nombre}.xml'}"], cwd=wt, env=cfg["env"], check=False)
    (raw / f"pytest-{nombre}.log").write_text(r.stdout[-20000:] + r.stderr[-5000:])
    (raw / f"tests-{nombre}.json").write_text(json.dumps(junit(raw / f"junit-{nombre}.xml")) + "\n")
    covrc.unlink(missing_ok=True)
    productivo = [p for p in cfg["productivo"] if (wt / p).exists()]
    print(f"[{nombre}] ruff C901…", flush=True)
    r = sh([str(py), "-m", "ruff", "check", "--select", "C901", "--config", "lint.mccabe.max-complexity = 10",
            "--ignore-noqa", "--exit-zero", "--output-format", "json", *productivo], cwd=wt, check=False)
    (raw / f"cc-ruff-{nombre}.json").write_text(r.stdout or "[]")
    print(f"[{nombre}] radon…", flush=True)
    r = sh([str(py), "-m", "radon", "cc", "-j", *productivo], cwd=wt)
    (raw / f"cc-radon-{nombre}.json").write_text(r.stdout)


def medir_frontend(cfg: dict, wt: Path, raw: Path) -> None:
    print("[frontend] pnpm install…", flush=True)
    sh(["pnpm", "install", "--frozen-lockfile", "--silent"], cwd=wt)
    if not (wt / "node_modules" / "@vitest" / "coverage-v8").exists():
        ver = sh(["node", "-p", "require('./node_modules/vitest/package.json').version"], cwd=wt).stdout.strip()
        sh(["pnpm", "add", "-D", f"@vitest/coverage-v8@{ver}", "--silent"], cwd=wt)
    print("[frontend] vitest con cobertura…", flush=True)
    r = sh(["pnpm", "exec", "vitest", "run", "--coverage", "--coverage.provider=v8",
            "--coverage.include=src/**", "--coverage.exclude=src/**/__tests__/**", "--coverage.exclude=src/**/*.d.ts",
            "--coverage.reporter=json-summary", "--coverage.reporter=lcov",
            f"--coverage.reportsDirectory={raw / 'cov-frontend'}",
            "--reporter=default", "--reporter=json", f"--outputFile.json={raw / 'vitest-frontend.json'}"],
           cwd=wt, check=False)
    (raw / "vitest-frontend.log").write_text(r.stdout[-20000:] + r.stderr[-5000:])
    shutil.copy(raw / "cov-frontend" / "coverage-summary.json", raw / "cobertura-frontend.json")
    vj = json.loads((raw / "vitest-frontend.json").read_text())
    (raw / "tests-frontend.json").write_text(json.dumps({
        "total": vj.get("numTotalTests"), "aprobados": vj.get("numPassedTests"),
        "fallidos": vj.get("numFailedTests"), "archivos": vj.get("numTotalTestSuites")}) + "\n")
    print("[frontend] eslint complexity…", flush=True)
    r = sh(["pnpm", "exec", "eslint", "--no-inline-config", "--rule", 'complexity: ["error", 0]',
            "--format", "json", "src"], cwd=wt, check=False)
    (raw / "cc-eslint-frontend.json").write_text(r.stdout or "[]")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("repo", choices=sorted(REPOS))
    ap.add_argument("--carpeta", required=True, help="nombre bajo mediciones/, p. ej. 2026-10-22-antes")
    ap.add_argument("--ref", default="origin/main")
    args = ap.parse_args()

    cfg = REPOS[args.repo]
    raw = HUB / "mediciones" / args.carpeta / "raw"; raw.mkdir(parents=True, exist_ok=True)
    wt = HUB / ".tmp" / f"wt-{args.repo}"
    commit = worktree(cfg["ruta"], args.ref, wt)
    print(f"[{args.repo}] worktree en {wt} @ {commit} ({args.ref})", flush=True)
    try:
        if args.repo == "frontend":
            medir_frontend(cfg, wt, raw)
        else:
            medir_python(args.repo, cfg, wt, raw)
        (raw / f"meta-{args.repo}.json").write_text(json.dumps({
            "commit": commit, "ref": args.ref, "fecha": __import__("datetime").date.today().isoformat()}) + "\n")
    finally:
        limpiar(cfg["ruta"], wt)
    subprocess.run([sys.executable, str(HUB / "scripts" / "resumir.py"), str(HUB / "mediciones" / args.carpeta)], check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
