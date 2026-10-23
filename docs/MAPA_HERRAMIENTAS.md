# Mapa de herramientas del ecosistema de pruebas de OnTimeAI

Misma tabla que la cátedra usó para el ecosistema, aplicada al proyecto. En
negrita, las incorporadas durante el TP.

| Categoría | Qué resuelve | Herramienta en OnTimeAI | Dónde |
|---|---|---|---|
| Gestión de pruebas y defectos | planificar, trazar, registrar | GitHub Issues con formulario "Defecto", GitHub Projects, este repo (plan, trazabilidad) | los tres repos, hub |
| Análisis estático | revisar sin ejecutar | ruff (C901 y reglas de bug), ESLint, `tsc`, **gate de complejidad con trinquete**, **jscpd** (duplicación) | `ci.yml` |
| Cobertura | qué ejecutan las pruebas | pytest-cov con ramas, @vitest/coverage-v8, **diff-cover** (sobre código nuevo) | `ci.yml` |
| Ejecución y registro | correr y reportar | pytest, vitest, GitHub Actions (resumen del job, artifacts) | `ci.yml` |
| API e integración | contratos entre servicios | `TestClient` de FastAPI, dobles de GCS/FR24/AeroAPI, **prueba real de GCS con CAS** | `tests/`, `integration.yml` |
| Rendimiento | carga, stress, escalabilidad | **k6** (smoke, stress, soak) | `stress.yml`, `k6/` |
| Smoke y aceptación | el despliegue nuevo responde | `curl` contra Cloud Run, **`/health`** | `smoke.yml` tras `deploy.yml` |
| Observabilidad en producción | detectar fallas en operación | vigía (`watchdog.py`) con Telegram, keepalive | Cloud Run Job + Scheduler |
| Build y despliegue | reproducibilidad | Docker, Cloud Build, Cloud Run, Workload Identity, Capacitor | `deploy.yml`, `android-build.yml`, `ios-*.yml` |
| Datos de prueba | entornos controlados | `live_data.db` bundleada, siembra de vuelos (`make_fixture_db.py`), bases temporales | `tests/`, `scripts/` |
| IA en QA | generar y revisar | Claude Code para generar tests, scripts y documentación; el grupo ejecuta y explica cada pieza | todo el TP |

## Decisiones de selección

- **k6** fue la incorporación con proceso de cinco pasos ([HERRAMIENTA_K6.md](HERRAMIENTA_K6.md)).
- **SonarQube Cloud** se evaluó como tablero; el quality gate corre en el
  propio pipeline (ruff/ESLint, jscpd, diff-cover) para no depender de un SaaS
  para bloquear un merge. Si el tablero se habilita, consume los mismos
  reportes de cobertura.
- **JMeter** y **Locust** quedaron en la shortlist de carga; **Cypress** y
  **Playwright** quedaron fuera del alcance del TP por el orden de corte.
