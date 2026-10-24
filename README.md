# OnTimeAI-Calidad

Repositorio hub del **TP Integrador de Calidad de Software** (UCC, 2026) aplicado
a la tesis OnTimeAI. Acá viven el plan de pruebas, la matriz ISO/IEC 25010, los
riesgos, la trazabilidad, el registro de la herramienta incorporada, las
mediciones de antes y después y el informe. El código de las pruebas y los
pipelines viven en cada repo, donde corren:

| Repo | Qué es | CI |
|---|---|---|
| [OnTimeAI-Backend](https://github.com/santiago6124/OnTimeAI-Backend) | API FastAPI, modelo LightGBM, jobs de inferencia, vigía | `ci.yml`, `deploy.yml`, `smoke.yml`, `stress.yml` (k6) |
| [OnTimeAI-Scrapper](https://github.com/santiago6124/OnTimeAI-Scrapper) | harvester FR24/OpenSky, base live en GCS | `ci.yml`, `deploy.yml`, `integration.yml` (GCS real) |
| [OnTimeAI-Frontend](https://github.com/santiago6124/OnTimeAI-Frontend) | dashboard Next.js, apps Capacitor | `ci.yml`, `deploy.yml`, móviles |

## Estructura

```
docs/          plan de pruebas, objetivos, riesgos, contingencia, QA vs QC, ISO 25010,
               casos, trazabilidad, defectos, herramienta (k6), evidencia de CI, demo
mediciones/    una carpeta por fecha y etiqueta, con crudos y resumen
scripts/       medir.py (reproduce una medición) y resumir.py (la resume)
informe/       fuente del informe y PDF
```

## Reproducir una medición

```bash
python3.12 -m venv .venvs/backend  && .venvs/backend/bin/pip  install -r ../OnTimeAI-Backend/requirements-api.txt -r ../OnTimeAI-Backend/requirements-job.txt -r ../OnTimeAI-Backend/requirements.txt pytest-cov ruff==0.17.2 radon==6.0.1
python3.12 -m venv .venvs/scrapper && .venvs/scrapper/bin/pip install -r ../OnTimeAI-Scrapper/requirements.txt pytest pytest-cov ruff==0.17.2 radon==6.0.1
python3 scripts/medir.py backend  --carpeta 2026-10-26-despues
python3 scripts/medir.py scrapper --carpeta 2026-10-26-despues
python3 scripts/medir.py frontend --carpeta 2026-10-26-despues
```

Cada corrida crea un worktree temporal del repo en `origin/main` (o `--ref`),
corre la suite con cobertura de líneas y ramas, mide complejidad ciclomática y
escribe `mediciones/<carpeta>/raw/` más `resumen.md` y `resumen.json`. Los
números del informe salen de esos resúmenes, nunca se tipean a mano.

Definición de cobertura: se mide sobre **el código desplegado** de cada repo
(lo que copian sus Dockerfiles; en el Frontend, `src/`), con líneas y ramas.
Es el mismo alcance que el gate de complejidad y que `[tool.coverage.run]
source` del CI, así que el número local y el del pipeline coinciden.
