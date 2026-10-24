# Plan de contingencia ante la caída de una dependencia crítica

OnTimeAI depende de servicios que no controla. Para cada uno: cómo se detecta
la caída, qué pasa mientras dura, cómo se degrada el servicio y cómo se
recupera. Los tiempos objetivo salen de [OBJETIVOS_DE_CALIDAD.md](OBJETIVOS_DE_CALIDAD.md)
(OO-01: alerta en ≤ 30 min; OO-02: recuperación en ≤ 1 h).

## Mapa de dependencias

```
FR24 ──────────┐
OpenSky ───────┤→ harvester ──→ live_data.db en GCS ──→ live-pull / live-pull-2 ──→ API ──→ Frontend / apps
IEM (METAR) ───┤                                        ↑ AeroAPI (fallback de features)
FAA NAS ───────┘                                        ↑ Firebase Auth (login con Google/correo)
```

## Dependencia crítica 1: FR24 (fuente primaria de vuelos)

| | |
|---|---|
| Qué se pierde | vuelos nuevos, estimados y cierres de outcomes; en 2 h no hay predicciones frescas |
| Detección | vigía: frescura por fuente (#44), alerta Telegram si `flights` no recibe filas en 30 min; canary `validate_sources.py --check fr24-airport` programado |
| Modo degradado | el harvester cae a OpenSky para posiciones y a AeroAPI para horarios (`LIVE_DATA_SOURCE=aeroapi` en los predictores restaura la ingesta anterior sin reconstruir la imagen) |
| Recuperación | si FR24 cambió formato: ajustar `fr24_client.normalize_flight` con los fixtures de `tests/`; si bloqueó el fingerprint: rotar `curl_cffi` (`chrome136` → versión siguiente); redeploy automático al mergear |
| Evidencia previa | FR24 cambia el ID hexadecimal entre seguimiento y cierre; la reconciliación de aliases existe desde el 2026-08-12 |
| Pruebas | `test_future_legs.py`, `test_horario_futuro.py`, canary FR24 (CP-INT-02) |

## Dependencia crítica 2: Google Cloud Storage (base compartida)

| | |
|---|---|
| Qué se pierde | nada se escribe ni se lee; API sirve la última copia descargada (`/tmp/live_data.db`) hasta que caduca |
| Detección | errores 403/5xx en el download del job (reintentos con deadline, #31); vigía mide trabajo pendiente (#66) |
| Modo degradado | la API sigue respondiendo con la última base refrescada; los jobs reintentan y abandonan sin corromper (CAS falla cerrado) |
| Recuperación | si la generación quedó corrupta: `quick_check` la rechaza y se restaura la anterior desde soft delete (7 días); si el proyecto queda inoperable (billing): migración al proyecto `ontimeai-prod` (hecha el 2026-08-19), con bucket, registry y service accounts nuevos |
| Evidencia previa | base corrupta 2026-06-08; proyecto `ontimeai` muerto por billing el 2026-08-19 |
| Pruebas | `test_gcs_generation.py` (dobles), CP-INT-01 contra bucket real, `test_live_job_generation.py` |

## Dependencia crítica 3: Cloud Run (servicio y jobs)

| | |
|---|---|
| Detección | smoke post-deploy; keepalive cada 10 min sobre `/docs`; vigía con duración y tamaño (#48) |
| Modo degradado | una sola instancia: si cae, no hay API hasta la revisión siguiente; las apps muestran el último estado cargado |
| Recuperación | rollback de tráfico a la revisión anterior (`gcloud run services update-traffic --to-revisions`), ≤ 10 min; redeploy desde `main` con `workflow_dispatch` |

## Dependencias secundarias

| Dependencia | Si cae | Mitigación |
|---|---|---|
| IEM (METAR) | features de clima vacías; el modelo las tolera como faltantes | cache de clima por red (#38) y por frescura (#70, #74); IEM 503 tolerado en el ciclo |
| FAA NAS | sin estado de programa de demoras | parser tolerante; vigía mide si la FAA contesta (#75) |
| AeroAPI / Aviationstack | sin fallback de horarios; cuota | fase 4 hace a FR24 primaria; claves validadas sólo por presencia |
| Firebase Auth | sin login con Google ni correo | login con usuario y contraseña locales sigue operativo; viewer y admin existen por variables de entorno |
| ADS-B (airplanes.live) | sin holding ni ETA por posición | muerto desde el 2026-08-12 sin impacto en AUC; las dos etapas de ajuste quedan inertes |

## Simulacro

Una vez por mes: cortar la variable `GCS_BUCKET` de `ontimeai-live-pull-2` en
una ejecución manual y verificar que (a) el vigía alerta, (b) el job termina sin
subir nada y (c) la API sigue sirviendo. Resultado esperado y obtenido se
registran como caso de prueba CP-CONT-01.
