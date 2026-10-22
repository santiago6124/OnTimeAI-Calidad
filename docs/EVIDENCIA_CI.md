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
