# Análisis estático y métricas interpretadas

Qué corre, qué mide y qué dicen los números. Las mediciones son las de
`mediciones/2026-10-22-antes` (línea de base, `origin/main` de cada repo) y
los runs del CI citados en [EVIDENCIA_CI.md](EVIDENCIA_CI.md). Las herramientas
están fijadas en versión en cada repo para que local y CI cuenten igual.

## Qué corre en cada PR

| Herramienta | Qué detecta | Backend | Scrapper | Frontend | Bloquea |
|---|---|---|---|---|---|
| ruff C901 (McCabe) | funciones nuevas con complejidad > 10; crecimiento de las exentas | sí | sí | ESLint `complexity` | sí (trinquete) |
| ruff E9 / F63 / F7 / F82 | sintaxis, nombres indefinidos, redefiniciones, comparaciones inválidas | sí | sí | ESLint + `tsc` | sí |
| jscpd | duplicación de bloques (≥ 50 tokens, ≥ 5 líneas) | sí | sí | sí | sí (> 5 %) |
| pytest-cov / v8 | cobertura de líneas y de ramas (decisión) | sí | sí | sí | sí (trinquete) |
| diff-cover | cobertura de las líneas cambiadas por el PR | sí | sí | sí | sí (< 80 %) |
| radon | distribución de complejidad por rango, promedio, top | sí | sí | — | no (reporte) |

## Métricas de producto, interpretadas

### Tamaño y complejidad (código desplegado)

| Repo | Líneas medibles | Bloques | Promedio CC | > 10 | > 15 | > 20 | Peor |
|---|---|---|---|---|---|---|---|
| Backend | 6.553 | 383 | 5,93 (B) | 46 | 24 | 11 | `live_pull.py:main` 72 (ruff) / 157 (radon) |
| Scrapper | 1.295 | 87 | 6,03 (B) | 12 | 6 | 4 | `select_tails_to_hydrate` 24 / 41 |
| Frontend | 2.534 | 1.218 funciones | 2,34 | 36 | 17 | 4 | `CascadaCard` 32 |

Dónde se concentra: en el Backend, las 11 funciones por encima de 20 están
en cinco archivos (`live_pull.py`, `training_store.py`, `live.py`,
`faa_nas.py`, `lineage_fallback.py`), y el promedio bajo (5,9) esconde esa
cola. En el Frontend el promedio es muy bajo porque React genera cientos de
funciones de una línea; las 36 que superan 10 son componentes de página con
mucha lógica condicional de render (`CascadaCard`, `TestCasesViewer`,
`FlightsTableView`). Consecuencia: el riesgo no está repartido, está en pocas
funciones, y por eso el gate es un trinquete y no una meta de promedio.

### Duplicación

| Repo | Líneas duplicadas | Clones | Umbral |
|---|---|---|---|
| Backend | 0,89 % (64 de 7.177) | 7 | 5 % |
| Scrapper | 0 % | 0 | 5 % |
| Frontend | (ver PR de cobertura) | | 5 % |

Los siete clones del Backend están en `faa_nas.py` (parseo de dos bloques
XML casi iguales) y en `training_store.py`. Ninguno justifica intervenir
antes que la complejidad.

### Cobertura de sentencia y de decisión

| Repo | Líneas | Ramas | Lectura |
|---|---|---|---|
| Backend | 52,6 % | 42,8 % | la mitad del código desplegado tiene tests; la cobertura de decisión es diez puntos menor: los `if` de los caminos de error son los menos ejercitados. `live_pull.py` (6 %) y `faa_nas.py` (0 %) son los huecos. |
| Scrapper | 50,7 % | 33,7 % | `harvester.py` al 25 % y `backfill_outcomes.py` al 0 %: el ciclo principal se prueba por partes, nunca entero. |
| Frontend | 17,6 % | 13,7 % | sólo `src/lib` y los handlers de API tienen tests; páginas y componentes están en 0 %. |

### Bugs de análisis estático

| Repo | Hallazgos | Qué |
|---|---|---|
| Backend | 1 → 0 | `F821 download_faa_registry` en `adsb_lineage.py` (DEF-01), latente desde el primer commit del módulo |
| Scrapper | 0 | — |
| Frontend | 0 | ESLint con `eslint-config-next` y `tsc` ya corrían |

## Métrica de proceso y de proyecto

De `mediciones/proceso-2026-10-23.md`, calculadas con `scripts/metricas_proceso.py`:

| Métrica | Tipo | Backend | Scrapper | Frontend | Lectura |
|---|---|---|---|---|---|
| Lead time de PR (mediana) | proceso | 0,1 h | 0,2 h | 0,0 h | una sola persona abre y mergea: no hay cola de revisión. Es rápido, pero el TP introduce la revisión cruzada como criterio de salida |
| Fixes con test de regresión | proceso | 77 % | 78 % | 31 % | en Python la práctica está instalada; en el Frontend los fixes son de CSS y layout y no se automatizan |
| Duración del CI (mediana) | proceso | 1,6 min | 0,4 min | 1,1 min | muy por debajo del objetivo OE-01 de 10 min; hay margen para los gates nuevos |
| PRs mergeados por semana (últimas 8) | proyecto | 0 8 38 7 5 3 6 1 | 0 0 7 4 3 0 1 2 | 3 4 12 8 5 6 2 18 | el pico de 38 en el Backend fue la semana de la auditoría de septiembre; el Frontend tuvo su pico con el rediseño |

## Decisión sobre SonarQube

Se evaluó SonarQube Cloud (gratis para repos públicos) como tablero. No se
adoptó dentro del TP: exige una cuenta y un token por repo que sólo puede
crear el dueño de la organización de GitHub, y el quality gate que pide la
cátedra (bugs críticos, duplicación > 5 %, cobertura sobre código nuevo < 80 %)
se implementó dentro del propio pipeline con ruff/ESLint, jscpd y diff-cover,
sin depender de un servicio externo para bloquear un merge (riesgo RY-05).
Los reportes XML y LCOV que ya genera el CI son los mismos que Sonar
consumiría, así que habilitarlo después es agregar un paso, no rehacer nada.
