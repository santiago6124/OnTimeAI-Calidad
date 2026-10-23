# Evidencia de ejecuciones del pipeline

El TP pide al menos una ejecución completa en verde y una fallida que haya
detectado un problema real. Se registran acá a medida que ocurren, con el run
de GitHub Actions como fuente.

## Antes del TP (historial de los repos)

| Repo | Run | Resultado | Qué detectó |
|---|---|---|---|
| Backend | PR #87, 2026-10-16 | rojo | el fixture de `test_api.py` apuntaba a `/tmp/live_data.db`, que no existe en el runner: pasaba en local y fallaba en CI |
| Scrapper | run 34708236989, 2026-09-12 | rojo | `ModuleNotFoundError: ontimeai_scrapper`: pytest no agregaba la raíz al `sys.path`; corregido con `pytest.ini` |
| Backend, Scrapper, Frontend | últimos 100 runs al 2026-10-22 | 99/1, 36/1, 100/0 | — |

## Durante el TP

| Fecha | Repo | PR | Run | Resultado | Qué detectó |
|---|---|---|---|---|---|
| 2026-10-22 | Backend | [#89](https://github.com/santiago6124/OnTimeAI-Backend/pull/89) gate de complejidad | [39865154889](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/39865154889) | **rojo** | 21 funciones productivas por encima de complejidad 10; la peor `live_pull.py:main` con 72 |
| 2026-10-22 | Backend | #89 | [39865674416](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/39865674416) | verde | deuda registrada en la baseline; sin deuda nueva |
| 2026-10-22 | Scrapper | [#19](https://github.com/santiago6124/OnTimeAI-Scrapper/pull/19) gate de complejidad | [39865894222](https://github.com/santiago6124/OnTimeAI-Scrapper/actions/runs/39865894222) | **rojo** | 4 funciones productivas por encima de 10: `_run_once` 24, `select_tails_to_hydrate` 24, `reconcile_fr24_flight_aliases` 16, `fetch_aircraft_history` 12 |
| 2026-10-22 | Scrapper | #19 | [39866231297](https://github.com/santiago6124/OnTimeAI-Scrapper/actions/runs/39866231297) | verde | baseline con 4 exentas; 80 tests |
| 2026-10-22 | Frontend | [#74](https://github.com/santiago6124/OnTimeAI-Frontend/pull/74) gate de complejidad | [39866296975](https://github.com/santiago6124/OnTimeAI-Frontend/actions/runs/39866296975) | **rojo** | 36 funciones de `src/` por encima de 10 (de 1.218 medidas, promedio 2,34): `CascadaCard` 32, `TestCasesViewer` 31, `POST /api/ota/updates` 23 |
| 2026-10-22 | Frontend | #74 | [39866806639](https://github.com/santiago6124/OnTimeAI-Frontend/actions/runs/39866806639) | verde | baseline con 36 exentas; lint, typecheck y 233 tests verdes |
| 2026-10-23 | Backend | [#91](https://github.com/santiago6124/OnTimeAI-Backend/pull/91) cobertura y quality gate | [40005299387](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40005299387) | **rojo** | gate "Bugs críticos": `F821 Undefined name download_faa_registry` en `feature_engineering_v7/adsb_lineage.py:367`, un `NameError` latente desde el primer commit del módulo (DEF-01, issue #90) |
| 2026-10-23 | Backend | #91 | [40006159701](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40006159701) | verde | defecto corregido con test de regresión; diff-cover 96 % sobre las líneas cambiadas; duplicación 0,89 % |
| 2026-10-23 | Backend | [#92](https://github.com/santiago6124/OnTimeAI-Backend/pull/92) smoke post-deploy | [40006249166](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40006249166) | **rojo** | contra producción: 6 de 7 checks; `/cascade/{id}` sin token devuelve 401, no 404. El criterio del check estaba mal, no la API: el endpoint exige autenticación aunque la memoria del workspace lo daba por público |
| 2026-10-23 | Backend | #92 | [40006493715](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40006493715) | verde | 7 de 7 checks contra la revisión `ontimeai-backend-00074-4cr` en 7 s |
| 2026-10-23 | Scrapper | [#20](https://github.com/santiago6124/OnTimeAI-Scrapper/pull/20) cobertura y quality gate | [40007232332](https://github.com/santiago6124/OnTimeAI-Scrapper/actions/runs/40007232332) | **rojo** | trinquete de cobertura: `Required test coverage of 54.0% not reached. Total coverage: 52.92%` (umbral fijado un punto arriba a propósito; ruff no encontró bugs en el Scrapper) |
| 2026-10-23 | Scrapper | #20 | [40007618395](https://github.com/santiago6124/OnTimeAI-Scrapper/actions/runs/40007618395) | verde | trinquete en la línea de base; duplicación 0 %; diff-cover 96 %; 97 tests |
| 2026-10-23 | Backend | #91 | [40007720084](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40007720084) | verde | cobertura medida sobre el código desplegado: 53,2 % líneas, 42,9 % ramas, 50,8 % combinado con el trinquete en 50 |
| 2026-10-23 | Scrapper | #20 | [40008301817](https://github.com/santiago6124/OnTimeAI-Scrapper/actions/runs/40008301817) | verde | cobertura alineada al paquete desplegado (`ontimeai_scrapper`), trinquete en 46 |
| 2026-10-23 | Scrapper | [#22](https://github.com/santiago6124/OnTimeAI-Scrapper/pull/22) integración GCS real | [40008474040](https://github.com/santiago6124/OnTimeAI-Scrapper/actions/runs/40008474040) | verde | compare-and-swap contra `ontimeai-prod-qa` con Workload Identity: 1 test, 6 pasos, 5,6 s |
| 2026-10-23 | Frontend | [#79](https://github.com/santiago6124/OnTimeAI-Frontend/pull/79) cobertura y quality gate | [40008157458](https://github.com/santiago6124/OnTimeAI-Frontend/actions/runs/40008157458) | **rojo** | trinquete de cobertura: `Coverage for lines (17.6%) does not meet global threshold (18%)` (y ramas, funciones y sentencias); umbral fijado un punto arriba a propósito |
| 2026-10-23 | Frontend | #79 | [40008563648](https://github.com/santiago6124/OnTimeAI-Frontend/actions/runs/40008563648) | verde | 15 pasos: thresholds 17/13/10/17, duplicación 1,27 %, bundle móvil, 243 tests |
| 2026-10-23 | Backend | [#94](https://github.com/santiago6124/OnTimeAI-Backend/pull/94) refactor medido | [40008502435](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40008502435) | verde | baseline de complejidad 21 → 20 exentas; diff-cover 94 % |
| 2026-10-23 | Scrapper | [#23](https://github.com/santiago6124/OnTimeAI-Scrapper/pull/23) cobertura: backfill, clientes ADS-B, errores del harvester | [40009886732](https://github.com/santiago6124/OnTimeAI-Scrapper/actions/runs/40009886732) | verde | 25 tests nuevos; paquete desplegado 47 → 61 % combinado (`backfill_outcomes.py` 0 → 92 %) |
| 2026-10-23 | Backend | #94 | [40010225421](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40010225421) | verde | segundo refactor medido: `_upload_create_only` 11 → 3; baseline 19 exentas |
| 2026-10-23 | Backend | #94 | [40010733527](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40010733527) | verde | tercer refactor medido: `apply_lineage_fallback` 23 → 4; baseline 18 exentas; diff-cover 84 % |
| 2026-10-23 | Backend | [#96](https://github.com/santiago6124/OnTimeAI-Backend/pull/96) cobertura: faa_nas, predict, watchdog, live_job | [40012315485](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40012315485) | verde | 137 tests nuevos; código desplegado 52,6 → 58,5 % líneas, 42,8 → 50,0 % ramas; dos defectos caracterizados (DEF-11, DEF-12) |
| 2026-10-23 | Frontend | [#80](https://github.com/santiago6124/OnTimeAI-Frontend/pull/80) cobertura: lib, handlers de API, hooks y providers | [40012489050](https://github.com/santiago6124/OnTimeAI-Frontend/actions/runs/40012489050) | verde | 246 tests nuevos; `src/` 17,6 → 32,9 % líneas, 13,7 → 24,9 % ramas; trinquete 32/24/20/32; dos defectos caracterizados (DEF-13, DEF-14) |
| 2026-10-23 | Backend | #96 | [40013521172](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40013521172) | verde | 22 tests más sobre `ontimeai/live.py` (AeroAPI, paginación, holding ADS-B, v8); con todo aplicado el Backend llega al 61,1 % de líneas |
| 2026-10-23 | Backend | [#95](https://github.com/santiago6124/OnTimeAI-Backend/pull/95) k6 stress y soak | [40011382323](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40011382323) | verde | dispatch desde la rama con soak de 10 min: stress p95 3,2 s a 22 req/s, soak p95 1,7 s con deriva +10 %, 0 % de errores; umbrales OK |
| 2026-10-23 | Backend | #95 | [40013672721](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40013672721) | verde | run del PR (smoke + stress) sobre el commit final; CI de tests también verde (563 aprobados) |

## Tras los merges a `main` (2026-10-23)

| Fecha | Repo | Workflow | Run | Resultado | Qué muestra |
|---|---|---|---|---|---|
| 2026-10-23 | Backend | Deploy → Smoke (`workflow_run`) | [40021794808](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40021794808) | verde | smoke disparado automáticamente tras el deploy: 7 de 7 checks contra la revisión `ontimeai-backend-00077-q42` recién desplegada |
| 2026-10-23 | Backend | CI en `main` | [40021365101](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40021365101) | verde | trinquete de cobertura a 59 con 59,02 % medido en CI (PR #101); después se dejó en 58 con un punto de margen |
| 2026-10-23 | Scrapper | Integración (`push` a `main`) | [40019663794](https://github.com/santiago6124/OnTimeAI-Scrapper/actions/runs/40019663794) | verde | compare-and-swap contra el GCS real, disparado por el merge de #22 |
| 2026-10-23 | Scrapper | CI en `main` | [40019892833](https://github.com/santiago6124/OnTimeAI-Scrapper/actions/runs/40019892833) | verde | trinquete de cobertura a 60 con 60,7 % medido (PR #24) |
| 2026-10-23 | Frontend | CI en `main` | [40019991726](https://github.com/santiago6124/OnTimeAI-Frontend/actions/runs/40019991726) | verde | gates y cobertura con trinquete 32/24/20/32 sobre `main` tras #80 |

Los deploys intermedios del Backend aparecen como `cancelled`: con varios merges
seguidos, GitHub conserva un solo run pendiente por grupo de concurrencia y
reemplaza el anterior por el más nuevo; el último de cada tanda desplegó y su
smoke corrió.
