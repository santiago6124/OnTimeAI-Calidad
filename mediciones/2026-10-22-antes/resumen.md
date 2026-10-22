# Medición `2026-10-22-antes`

| Repo | Commit | Tests | Cobertura líneas | Cobertura ramas | Funciones > 10 (gate) | Promedio CC (radon) | > 20 (radon) |
|---|---|---|---|---|---|---|---|
| backend | `416eef8` | — | 39.5 % (3869/9801) | 33.6 % | — | 6.41 | 24 |
| scrapper | `2697284` | — | 50.6 % (655/1295) | 33.4 % | — | 6.2 | 5 |
| frontend | `c9aa055` | 233 | 17.6 % (446/2533) | 13.72 % | — | — | — |

## backend: funciones más complejas

| CC | Función | Archivo |
|---|---|---|
| 157 | `main` | `live_pull.py:142` |
| 70 | `materialize_fixed_horizons` | `ontimeai/training_store.py:1481` |
| 45 | `main` | `scripts/backtest_bts.py:60` |
| 45 | `main` | `evaluar_recalibrado.py:93` |
| 41 | `_parse_nas_xml` | `ontimeai/faa_nas.py:151` |
| 40 | `compute_scorecard` | `scripts/data_quality_scorecard.py:32` |
| 35 | `main` | `live_metrics.py:59` |
| 34 | `_refresh` | `feature_engineering_v7/gdp_scraper.py:169` |
| 33 | `build_inference_frame` | `ontimeai/live.py:1490` |
| 30 | `main` | `unbiased_sample_live/live_pull_multi.py:120` |

## scrapper: funciones más complejas

| CC | Función | Archivo |
|---|---|---|
| 41 | `select_tails_to_hydrate` | `ontimeai_scrapper/lineage_cache.py:338` |
| 35 | `normalize_flight` | `ontimeai_scrapper/fr24_client.py:234` |
| 31 | `_run_once` | `ontimeai_scrapper/harvester.py:301` |
| 25 | `reconcile_fr24_flight_aliases` | `ontimeai_scrapper/db.py:659` |
| 21 | `main` | `scripts/validate_sources.py:521` |
| 18 | `get_airport_page` | `ontimeai_scrapper/fr24_client.py:115` |
| 16 | `fetch_aircraft_history` | `ontimeai_scrapper/fr24_http.py:60` |
| 15 | `check_faa_master` | `scripts/validate_sources.py:357` |
| 14 | `main` | `scripts/analyze_future_legs.py:46` |
| 14 | `_normalize_state` | `ontimeai_scrapper/opensky_client.py:132` |
