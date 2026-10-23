# Casos de prueba

Diseñados con las técnicas de caja negra de la materia (clases de
equivalencia, valores límite, tablas de decisión), con el resultado esperado
escrito **antes** de ejecutar. Cada caso apunta al test automatizado que lo
ejecuta y al requisito que cubre ([TRAZABILIDAD.md](TRAZABILIDAD.md)). La
cobertura de sentencia y de decisión se mide con `pytest-cov --cov-branch` y
con `@vitest/coverage-v8` (ramas); los totales están en `mediciones/`.

## Tabla de decisión: autenticación y autorización (Backend)

Condiciones del login: el usuario existe, está activo, la contraseña es
correcta. Con tres condiciones booleanas hay 8 combinaciones; las filas con
"existe = no" colapsan en una porque las otras condiciones no se evalúan.

| CP | existe | activo | contraseña | Esperado | Test | Resultado |
|---|---|---|---|---|---|---|
| CP-AUTH-01 | sí | sí | correcta | 200, token con rol | `test_auth_01_…` | ✅ |
| CP-AUTH-02 | no | — | — | 401 | `test_auth_02_…` | ✅ |
| CP-AUTH-03 | sí | no | correcta | 401 | `test_auth_03_…` | ✅ |
| CP-AUTH-04 | sí | sí | incorrecta | 401 | `test_auth_04_…` | ✅ |

Condiciones de la autorización en `/admin/users`: hay token, la firma es
válida, no venció, el rol es superadmin.

| CP | token | firma | vigente | superadmin | Esperado | Test | Resultado |
|---|---|---|---|---|---|---|---|
| CP-AUTH-05 | no | — | — | — | 401 | `test_auth_05_…` | ✅ |
| CP-AUTH-06 | sí | ajena | — | — | 401 | `test_auth_06_…` | ✅ |
| CP-AUTH-07 | sí | válida | no | sí | 401 | `test_auth_07_…` | ✅ |
| CP-AUTH-08 | sí | válida | sí | no | 403 | `test_auth_08_…` | ✅ |
| CP-AUTH-09 | sí | válida | sí | sí | 200 | `test_auth_09_…` | ✅ |

Clases de equivalencia del alta de usuarios: rol válido (`user`, `admin`,
`superadmin`) → 201; rol inválido (`root`, vacío) → 400 (CP-AUTH-10); usuario
duplicado → 409 (CP-AUTH-11); autodesactivación del superadmin → 400
(CP-AUTH-12). Archivo: `tests/test_tabla_decision_auth.py` (PR Backend #93).

## Valores límite: bandas de riesgo (Backend)

`risk_level(p, umbral)`: bajo si `p < umbral`, medio si `umbral ≤ p < 2·umbral`,
alto si `p ≥ 2·umbral`. Dos límites, cada uno con el valor exacto y sus dos
vecinos (`± 1e-9`).

| CP | Entrada (umbral 0,09) | Esperado | Resultado |
|---|---|---|---|
| CP-RISK-01 | 0,09 − ε · 0,09 · 0,09 + ε | bajo · medio · medio | ✅ |
| CP-RISK-02 | 0,18 − ε · 0,18 · 0,18 + ε | medio · alto · alto | ✅ |
| CP-RISK-03 | umbral `None`, `0`, `−0,5` (clase inválida) | se usa el umbral de respaldo | ✅ |
| CP-RISK-04 | p = 0 y p = 1 (extremos del dominio) | no rompe; bajo y alto | ✅ |

Archivo: `tests/test_valores_limite_riesgo.py` (PR Backend #93). Los límites
"en el valor exacto" ya estaban cubiertos por `tests/test_risk_level.py`
desde el PR #40; se agregan los vecinos y las clases inválidas.

## Valores límite: cola de outcomes pendientes (Scrapper)

`pending_outcome_tails` encola la matrícula si la llegada esperada venció hace
al menos 30 min (gracia) y no más de 36 h (ventana).

| CP | Entrada | Esperado | Resultado |
|---|---|---|---|
| CP-SCR-01 | llegada hace 29 / 30 / 31 min | fuera / dentro / dentro | ✅ |
| CP-SCR-02 | llegada hace 35 h / 36 h 1 min | dentro / fuera | ✅ |
| CP-SCR-03 | vencido pero con actual (clase "ya cerrado") | fuera | ✅ |
| CP-SCR-04 | vencido pero cancelado | fuera | ✅ |

Archivo: `tests/test_valores_limite_outcomes.py` (PR Scrapper #20).

## Tabla de decisión: cascada de rotaciones (Backend, existente)

La fuente de la demora que se propaga se decide por tres condiciones:

| CP | el vuelo aterrizó | se pasó `demora_min` | hay predicción | Fuente esperada | Test existente |
|---|---|---|---|---|---|
| CP-CASC-01 | sí | no | — | `real` | `test_usa_la_demora_real_cuando_el_vuelo_ya_aterrizo` |
| CP-CASC-02 | — | sí | — | `simulada` (gana sobre la real) | `test_la_demora_pasada_a_mano_gana_sobre_la_real` |
| CP-CASC-03 | no | no | sí | `estimada`, con aviso | `test_sin_demora_real_la_deriva_de_la_probabilidad_y_avisa` |
| CP-CASC-04 | no | no | no | respuesta explica por qué no hay cascada | `test_sin_demora_ni_prediccion_dice_por_que` |

Valores límite ya cubiertos en `tests/test_cascada.py`: 15 min de demora (por
debajo no propaga), los bordes de los tramos de holgura sin huecos, holgura
por debajo y por encima del rango, cero piernas, máximo de piernas.

## Análisis estático y gates (los tres repos)

| CP | Qué | Esperado | Evidencia |
|---|---|---|---|
| CP-EST-01 | ruff E9/F63/F7/F82 sobre el código desplegado | 0 hallazgos | run rojo 40005299387 con 1 (DEF-01), verde 40006159701 |
| CP-EST-02 | duplicación jscpd | ≤ 5 % | 0,89 % Backend |
| CP-CC-01 | trinquete de complejidad: función nueva > 10 | falla | `tests/test_complejidad.py::test_sin_baseline_toda_violacion_es_nueva` |
| CP-CC-02 | trinquete: exenta que crece | falla | `test_exenta_que_crece_falla` |
| CP-CC-03 | trinquete: `--actualizar-baseline` con crecimiento | se rechaza | `test_actualizar_baseline_solo_achica` |
| CP-COB-01 | cobertura sobre líneas cambiadas | ≥ 80 % | diff-cover 96 % en PR #91 |

## Smoke post-deploy (Backend)

| CP | Check | Esperado | Resultado (run 40006493715) |
|---|---|---|---|
| CP-SMK-01 | `GET /docs` | 200 | ✅ |
| CP-SMK-02 | login con credenciales inválidas | 401 | ✅ |
| CP-SMK-03 | login viewer | 200 con token | ✅ |
| CP-SMK-04 | `/metrics/summary`, `/flights`, `/metrics/model`, `/metrics/hourly` | 200 con la forma esperada | ✅ |
| CP-SMK-05 | `/cascade/{id inexistente}` con token | 404 JSON | ✅ (el primer run, 40006249166, falló por un criterio mal escrito: sin token da 401) |

## Rendimiento (Backend, k6)

| CP | Escenario | Umbrales | Resultado |
|---|---|---|---|
| CP-PERF-01 | smoke: 1 VU, 30 s | checks 100 % | pendiente de PR |
| CP-PERF-02 | stress: 0 → 50 VU en 3 min | p95 bajo umbral, errores < 1 % | pendiente de PR |
| CP-PERF-03 | soak: 20 VU × 10 min | p95 estable, errores < 1 % | pendiente de PR |

## Integración externa

| CP | Qué | Esperado | Resultado |
|---|---|---|---|
| CP-INT-01 | GCS con CAS contra bucket real: subir, leer generación, subir con generación vieja, subir con la correcta | 412 en la vieja, 200 en la correcta | pendiente de workflow |
| CP-INT-02 | canary FR24 (`validate_sources.py --check fr24-airport`) | cobertura de campos ≥ 0,8 | pendiente |

## Defecto real con contraste rojo/verde

CP-FE-01: `tests/test_adsb_lineage.py::test_setup_descarga_y_construye_el_mapa_sin_explotar`
falla en el commit padre con `NameError` y pasa con el fix (DEF-01). Salida
completa en `mediciones/evidencia/DEF-01-adsb-lineage-rojo-verde.txt`.
