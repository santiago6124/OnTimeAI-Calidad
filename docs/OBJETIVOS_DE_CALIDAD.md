# Objetivos de calidad

Cada objetivo es medible, tiene fuente y una práctica de proceso que lo
sostiene. Las columnas "al inicio" y "al cierre" se llenan desde
`mediciones/` y desde la API de producción; nunca a mano.

## Desde el usuario (quien mira el dashboard o la app)

| ID | Objetivo | Métrica | Meta | Fuente | Práctica que lo sostiene |
|---|---|---|---|---|---|
| OU-01 | La predicción llega con tiempo para actuar | lead time mediano entre la primera predicción y la salida programada | ≥ 2 h en el 90 % de las salidas de ATL | `GET /metrics/lead-time` | harvester cada 15 min con `CAPTURE_FUTURE_LEGS`; predictores cada 15 min escalonados |
| OU-02 | La alerta es creíble | AUC y Brier sobre la ventana móvil de predicciones con label | AUC ≥ 0,75 y Brier ≤ 0,15 | `GET /metrics/model` | calibrador post-cadena; tests de calibración; umbral operativo calculado sobre la distribución que etiqueta |
| OU-03 | El dashboard responde | p95 de `GET /flights` y `GET /metrics/summary` bajo 20 usuarios concurrentes | p95 ≤ umbral fijado en `stress.yml` (medido en la PoC y documentado en `HERRAMIENTA_K6.md`) | k6 en CI | stress y soak en cada cambio de la API |
| OU-04 | Lo que se muestra en iOS es lo mismo que en la web | versión del bundle OTA en `production` igual a la del último release web | diferencia ≤ 1 versión | `POST /api/ota/updates` | `build-mobile.mjs --strict` en CI; publicación OTA tras cada release |

## Desde el equipo (quien cambia el código)

| ID | Objetivo | Métrica | Meta | Fuente | Práctica que lo sostiene |
|---|---|---|---|---|---|
| OE-01 | Feedback rápido | duración del job de CI | ≤ 10 min | GitHub Actions | tests sin red; base bundleada; cache de pip y pnpm |
| OE-02 | El código nuevo nace probado | cobertura sobre líneas cambiadas en cada PR | ≥ 80 % | `diff-cover` en CI | criterio de salida del PR |
| OE-03 | La cobertura del código existente no retrocede y crece | cobertura de líneas por repo | ≥ 60 % al cierre; nunca por debajo del trinquete | `mediciones/`, `--cov-fail-under` | trinquete que sólo sube |
| OE-04 | La complejidad no crece | funciones productivas con CC > 10 | sólo baja (21 / 4 / 36 al inicio) | gate de complejidad | baseline con trinquete |
| OE-05 | Cada defecto deja un test | fixes con test de regresión en el mismo PR | 100 % | git log, registro de defectos | plantilla de PR y de defecto |

## Desde la organización (quien paga y opera)

| ID | Objetivo | Métrica | Meta | Fuente | Práctica que lo sostiene |
|---|---|---|---|---|---|
| OO-01 | Nada se cae en silencio | tiempo entre la caída de una fuente y la alerta | ≤ 30 min | vigía (`watchdog.py`) y Telegram | frescura por fuente; smoke post-deploy |
| OO-02 | Recuperación acotada | tiempo desde un deploy roto hasta el rollback | ≤ 1 h | `deploy.yml` y registro de defectos | smoke post-deploy; revisiones de Cloud Run conservadas |
| OO-03 | Costo contenido | gasto mensual de GCP | sin crecimiento por el TP | facturación de GCP | stress sólo en el runner; imágenes reducidas |
| OO-04 | Datos para entrenar sin pisar producción | eventos publicados al training store por ciclo | > 0 en cada ciclo ganador | ledger GCS | outbox transaccional con acknowledge |

## Valores

| ID | Al inicio (2026-10-22) | Al cierre | Cumplido |
|---|---|---|---|
| OU-01 | pendiente de leer en producción | | |
| OU-02 | AUC 0,79 / Brier 0,195 sobre `proba_delay` (medición del 2026-09-06, antes del calibrador post-cadena) | | |
| OU-03 | sin medir | p95 11,1 s a 50 VUs y 6,8 s a 20 VUs con un proceso (k6, PoC local); 0 % de errores | no: DEF-15 |
| OE-01 | Backend ≈ 4 min, Scrapper ≈ 1 min, Frontend ≈ 2 min | mediana 1,6 / 0,4 / 1,1 min; con los gates nuevos, < 3 min | sí |
| OE-03 | 52,6 % / 50,7 % / 17,6 % de líneas (código desplegado) | 61,1 % / 64,8 % / 32,9 % (todos los PRs aplicados, 2026-10-23) | Backend y Scrapper sí; Frontend no |
| OE-04 | 21 / 4 / 36 | 18 / 4 / 36 | sí (sólo bajó) |
| OE-05 | 15 de los últimos 15 fixes del Backend con test | 77 % / 78 % / 31 % sobre todos los fixes históricos (`mediciones/proceso-2026-10-23.md`) | parcial: el Frontend arrastra fixes de CSS sin test |
