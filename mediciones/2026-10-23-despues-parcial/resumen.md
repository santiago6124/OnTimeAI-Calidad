# Medición `2026-10-23-despues-parcial`

| Repo | Commit | Tests | Cobertura líneas | Cobertura ramas | Funciones > 10 (gate) | Promedio CC (radon) | > 20 (radon) |
|---|---|---|---|---|---|---|---|
| backend | `ca956bf` | 589 | 53.5 % (3510/6557) | 43.2 % | 20 | 5.89 | 11 |
| scrapper | `097b909` | 105 | 50.6 % (655/1295) | 33.4 % | 4 | 6.03 | 4 |
| frontend | `97ec2bc` | 243 | 17.6 % (446/2534) | 13.71 % | 36 | 2.34 | 4 |

## backend: funciones más complejas

| CC | Función | Archivo |
|---|---|---|
| 157 | `main` | `live_pull.py:142` |
| 70 | `materialize_fixed_horizons` | `ontimeai/training_store.py:1495` |
| 41 | `_parse_nas_xml` | `ontimeai/faa_nas.py:151` |
| 34 | `_refresh` | `feature_engineering_v7/gdp_scraper.py:169` |
| 33 | `build_inference_frame` | `ontimeai/live.py:1490` |
| 29 | `publish_pending_outbox` | `ontimeai/training_store.py:1230` |
| 29 | `prepare_silver_training_data` | `ontimeai/training_store.py:1982` |
| 28 | `_add_v7_wind_features` | `ontimeai/live.py:1761` |
| 26 | `apply_lineage_fallback` | `ontimeai/lineage_fallback.py:155` |
| 23 | `aeroapi_to_flight_row` | `ontimeai/live.py:676` |

## scrapper: funciones más complejas

| CC | Función | Archivo |
|---|---|---|
| 41 | `select_tails_to_hydrate` | `ontimeai_scrapper/lineage_cache.py:338` |
| 35 | `normalize_flight` | `ontimeai_scrapper/fr24_client.py:234` |
| 31 | `_run_once` | `ontimeai_scrapper/harvester.py:301` |
| 25 | `reconcile_fr24_flight_aliases` | `ontimeai_scrapper/db.py:659` |
| 18 | `get_airport_page` | `ontimeai_scrapper/fr24_client.py:115` |
| 16 | `fetch_aircraft_history` | `ontimeai_scrapper/fr24_http.py:60` |
| 14 | `_normalize_state` | `ontimeai_scrapper/opensky_client.py:132` |
| 14 | `normalize_actual` | `ontimeai_scrapper/fr24_client.py:343` |
| 12 | `maybe_hydrate_tail` | `ontimeai_scrapper/lineage_cache.py:143` |
| 12 | `harvest_chain_walk` | `ontimeai_scrapper/harvester.py:190` |

## frontend: funciones más complejas

| CC | Función | Archivo |
|---|---|---|
| 32 | `Function 'CascadaCard'` | `components/cascada-card.tsx:72` |
| 31 | `Function 'TestCasesViewer'` | `app/tesis/pruebas/page.tsx:159` |
| 23 | `Async function 'POST'` | `app/api/ota/updates/route.ts:117` |
| 22 | `Arrow function` | `components/ui/chart.tsx:204` |
| 20 | `Function 'PredictionEvolution'` | `components/prediction-evolution.tsx:19` |
| 19 | `Function 'flightToTrack'` | `hooks/use-real-flight-tracks.ts:37` |
| 19 | `Function 'FlightsTableView'` | `components/flights-table.tsx:85` |
| 19 | `Function 'FlightRow'` | `components/flights-table.tsx:338` |
| 19 | `Function 'WeatherPage'` | `app/weather/page.tsx:32` |
| 19 | `Async function 'ReportsPage'` | `app/reports/page.tsx:39` |
