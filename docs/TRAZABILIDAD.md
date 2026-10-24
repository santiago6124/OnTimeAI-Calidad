# Trazabilidad requisito → caso de prueba → defecto

Los requisitos salen del anteproyecto de OnTimeAI y del comportamiento que el
sistema ya tiene en producción. Los casos están en
[CASOS_DE_PRUEBA.md](CASOS_DE_PRUEBA.md) y los defectos en
[DEFECTOS.md](DEFECTOS.md).

## Requisitos

| ID | Requisito | Repo |
|---|---|---|
| RF-01 | Predecir la probabilidad de demora de llegada (> 15 min) de cada vuelo que sale de ATL, con calibración medible | Backend |
| RF-02 | Explicar cada predicción (SHAP) y mantener la identidad del vuelo entre ciclos | Backend |
| RF-03 | Proyectar la cascada de demoras por rotación de la aeronave | Backend |
| RF-04 | Autenticar usuarios por JWT con roles (user, admin, superadmin) y por Google/Firebase | Backend, Frontend |
| RF-05 | Exponer métricas agregadas (resumen, por hora, modelo, rutas, lead time) | Backend, Frontend |
| RF-06 | Perfil Viajero: guardar vuelos y recibir alertas de clima | Backend, Frontend |
| RF-07 | Ingerir vuelos y rotaciones desde FR24 con fallback OpenSky, y cerrar outcomes pendientes | Scrapper |
| RF-08 | Compartir la base live entre jobs sin corromperla (CAS por generación) | Scrapper, Backend |
| RNF-01 | La API responde bajo carga concurrente dentro de umbrales de latencia y error | Backend |
| RNF-02 | El pipeline no se cae en silencio: alertas y smoke tras cada deploy | Backend |
| RNF-03 | Secretos sólo por entorno; nunca valores por defecto | Backend |
| RNF-04 | Las apps móviles sirven la misma versión que la web | Frontend |
| RNF-05 | Mantenibilidad: sin funciones nuevas con complejidad > 10, sin bugs de análisis estático, duplicación ≤ 5 %, cobertura con trinquete | los tres |
| RNF-06 | Accesibilidad: respetar "reducir movimiento" sin perder contenido | Frontend |

## Matriz

| Requisito | Casos de prueba | Tests automatizados | Defectos asociados |
|---|---|---|---|
| RF-01 | CP-RISK-01..04, CP-CAL-01, CP-LIVE-02, CP-COB-01..02 | `test_valores_limite_riesgo.py`, `test_risk_level.py`, `test_chain_calibration.py`, `test_operational_threshold.py`, `test_clima_fresco.py`, `test_faa_nas.py`, `test_predict.py` | DEF-02, DEF-04, DEF-06, DEF-11, DEF-12 |
| RF-02 | CP-LIVE-01 | `test_stable_id.py`, `test_explainability.py`, `test_shap_nativo.py` | DEF-05 |
| RF-03 | CP-CASC-01..04 | `test_cascada.py`, `test_cascada_endpoint.py` | — |
| RF-04 | CP-AUTH-01..12, CP-COB-FE | `test_tabla_decision_auth.py`, `test_auth_google.py`, `test_auth_firebase.py`, `route.test.ts` del login | DEF-14 |
| RF-05 | CP-SMK-04, CP-API-01, CP-API-05, CP-COB-FE | `test_api.py`, `test_ventana_activa.py`, `test_optional_prediction_columns.py`, `fmt-time.test.ts` | DEF-06, DEF-07, DEF-13 |
| RF-06 | CP-API-09 | `test_modo_viajero.py`, `mis-vuelos-view.test.tsx` | DEF-03 |
| RF-07 | CP-SCR-01..04, CP-INT-02 | `test_valores_limite_outcomes.py`, `test_pending_outcomes.py`, `test_future_legs.py`, `test_horario_futuro.py` | DEF-08 |
| RF-08 | CP-INT-01 | `test_gcs_generation.py`, `test_live_job_generation.py`, `integration.yml` | — (incidente 2026-06-08 previo al registro) |
| RNF-01 | CP-PERF-01..03 | `stress.yml` (k6) | DEF-15 |
| RNF-02 | CP-SMK-01..05 | `smoke.yml`, `test_watchdog.py` | DEF-06 (origen del smoke) |
| RNF-03 | — | `conftest.py` exige los secretos; `test_api.py` | riesgo RP-06 |
| RNF-04 | CP-MOB-01 | `build-mobile.mjs --strict` en CI, `route.test.ts` del OTA | DEF-10 |
| RNF-05 | CP-EST-01..03, CP-CC-01..03, CP-FE-01 | `test_complejidad.py`, `test_calidad_resumen.py`, `test_adsb_lineage.py`, gates de `ci.yml` | DEF-01 |
| RNF-06 | CP-UI-01 (exploratorio) | — | DEF-09 |

## Lectura

- Todo requisito funcional tiene al menos un test automatizado; RF-03 y RF-04
  tienen además casos de diseño explícito (tabla de decisión).
- Los defectos de producción (DEF-02 a DEF-07) se concentran en RF-01 y RF-05,
  que son también los requisitos con más tests: coincide con el agrupamiento
  de defectos observado en `api.py`.
- Los cinco defectos que encontraron las pruebas nuevas (DEF-11 a DEF-15)
  salieron de tests de caracterización y de k6, no de producción: están
  abiertos, cada uno con el caso que lo reproduce.
- RNF-06 sólo tiene verificación exploratoria: es CSS y el costo de
  automatizarla (navegador real) no se amortiza con la frecuencia de cambio.
