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
