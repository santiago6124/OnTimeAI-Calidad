# Riesgos

Nivel = probabilidad × impacto, cada uno de 1 (bajo) a 5 (alto). Se revisa en
cada versión del plan de pruebas. Los riesgos con nivel ≥ 12 concentran el
esfuerzo de prueba; cada uno apunta a los casos que lo cubren
([CASOS_DE_PRUEBA.md](CASOS_DE_PRUEBA.md)) y a la evidencia que justifica la
probabilidad.

## Riesgos de producto

| ID | Riesgo | P | I | Nivel | Evidencia | Mitigación y pruebas |
|---|---|---|---|---|---|---|
| RP-01 | FR24 cambia el formato o bloquea al harvester: sin datos nuevos, sin predicciones | 3 | 5 | **15** | FR24 ya cambió IDs entre seguimiento y cierre (reconciliación de aliases, PR Scrapper del 2026-08-12); cliente con fingerprint `chrome136` | fallback OpenSky; canary FR24 (`validate_sources.py --check fr24-airport`); vigía con frescura por fuente y alertas Telegram; CP-INT-02 |
| RP-02 | Corrupción o pérdida de `live_data.db` en GCS (escrituras concurrentes de harvester y predictores) | 2 | 5 | **10** | incidente 2026-06-08 (base corrupta); 51 conflictos CAS en 24 h medidos el 2026-09-06 | CAS por generación con reintentos; `PRAGMA quick_check` antes de subir; soft delete 7 días; CP-INT-01 contra bucket real; `test_gcs_generation.py` |
| RP-03 | Un cambio deja el modelo peor calibrado sin que nadie lo note (la cadena de ajustes rompe la calibración) | 4 | 4 | **16** | Brier 0,133 crudo vs 0,195 tras ajustes (2026-09-06); umbral marcaba 46,6 % en vez de 22 % | calibrador post-cadena (#59, #86); `test_chain_calibration.py`, `test_operational_threshold.py`; métrica AUC/Brier en `/metrics/model` como objetivo de calidad |
| RP-04 | Predicciones huérfanas: vuelos predichos que nunca reciben label | 3 | 3 | 9 | 11,8 % huérfanas, subiendo de 2,9 % a 14,6 % entre tercios del período | `stable_id` (#65); cola de outcomes pendientes 36 h; `test_pending_outcomes.py`, `test_stable_id.py` |
| RP-05 | Ciclo del job supera la ventana entre corridas y se pisan las ejecuciones | 2 | 4 | 8 | ciclos de 4 a 10 min; cron reajustado a 8,23,38,53 | `docs/CICLO_Y_FRECUENCIA.md`; cronometrado por fase; watchdog mide duración (#48) |
| RP-06 | Secretos con valor por defecto: un deploy sin la variable arranca con el secreto commiteado | 1 | 5 | 5 | riesgo detectado en auditoría del 2026-09-06, corregido en #22 | `api.py` exige secretos sin default; CI define literales de prueba en `conftest.py`; CP-SEC-01 |
| RP-07 | La API deja de responder bajo carga (una sola instancia, 4 GiB) | 3 | 4 | **12** | instancia única fijada en #26; refresco de la base compite por CPU | k6 stress y soak con umbrales (p95, errores); CP-PERF-01..03; `--max-instances` conocido |
| RP-08 | Una función crítica muy compleja y casi sin tests concentra regresiones | 4 | 4 | **16** | `live_pull.py:main` CC 72 con 6 % de cobertura; 19 de 45 fixes en `api.py` | gate de complejidad con trinquete; tests de caracterización antes de refactorizar; cobertura con trinquete |
| RP-09 | Las apps iOS sirven un bundle OTA viejo respecto de la web | 3 | 2 | 6 | `production` en 1.0.2 pre-rediseño hasta el 2026-10-22 | `build-mobile.mjs --strict` en CI (#73); `route.test.ts` de `/api/ota/updates` |
| RP-10 | Dependencia de proveedores con cuota (AeroAPI, Aviationstack) agota el presupuesto | 2 | 3 | 6 | migración a FR24 como fuente primaria (fase 4) | `LIVE_DATA_SOURCE=harvester`; proveedores secundarios sólo como fallback |
| RP-11 | Identidades cruzadas entre proveedores (IDs FR24 vs. AeroAPI) producen joins incorrectos | 2 | 4 | 8 | IDs no intercambiables, documentado el 2026-08-12 | identidad operacional (vuelo, ruta, fecha, matrícula); `test_actual_provenance.py` |

## Riesgos de proyecto

| ID | Riesgo | P | I | Nivel | Mitigación |
|---|---|---|---|---|---|
| RY-01 | Plazo del TP (cuatro días) no alcanza para todos los ejes | 4 | 4 | **16** | orden de corte explícito en el plan: E2E, k6 contra Cloud Run, tests de componentes React |
| RY-02 | Un solo desarrollador activo concentra el conocimiento | 3 | 4 | **12** | documentación por decisión en `docs/` de cada repo; PRs con porqué |
| RY-03 | Costo de GCP crece por builds y stress | 2 | 2 | 4 | stress sólo en el runner; imágenes reducidas (#54, #55) |
| RY-04 | Cambios generados con IA que el grupo no puede explicar en la defensa | 3 | 5 | **15** | cada PR explica el porqué; el grupo ejecuta y lee cada herramienta; preguntas individuales ensayadas |
| RY-05 | Dependencia de SaaS externos para el gate (Sonar) | 2 | 3 | 6 | el quality gate corre en el propio pipeline (ruff/ESLint, jscpd, diff-cover); Sonar es tablero adicional |

## Matriz

```
Impacto 5 |        RP-06      RP-02     RP-01            
Impacto 4 |                   RP-05     RP-07 RY-02   RP-03 RP-08 RY-01 RY-04
Impacto 3 |                   RP-10     RP-04
Impacto 2 |                   RY-03     RP-09
Impacto 1 |
           ---------------------------------------------------
             P=1      P=2        P=3        P=4        P=5
```

Los cuatro riesgos de nivel 15 o 16 (RP-01, RP-03, RP-08, RY-01, RY-04) son los
que ordenan el plan: canary y fallback de FR24, calibración medida, gate de
complejidad con cobertura, y recorte explícito del alcance del TP.
