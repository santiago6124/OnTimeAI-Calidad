# Plan de pruebas de OnTimeAI

| Campo | Valor |
|---|---|
| Versión | 1.1 |
| Fecha | 2026-10-24 |
| Nivel declarado | **Nivel 2: prototipo parcial** (ver §2) |
| Repos cubiertos | OnTimeAI-Backend, OnTimeAI-Scrapper, OnTimeAI-Frontend |
| Documentos relacionados | [Objetivos de calidad](OBJETIVOS_DE_CALIDAD.md) · [Riesgos](RIESGOS.md) · [ISO/IEC 25010](ISO25010.md) · [Trazabilidad](TRAZABILIDAD.md) · [Casos de prueba](CASOS_DE_PRUEBA.md) · [Defectos](DEFECTOS.md) · [Contingencia](CONTINGENCIA.md) |

## Historial de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0 | 2026-10-22 | Primera versión: alcance, niveles, criterios de entrada y salida, entornos, métricas. Línea de base medida en `mediciones/2026-10-22-antes`. |
| 1.1 | 2026-10-24 | Cierre: trinquetes en su valor final, resultados de k6 e integración real, casos de regresión vinculados a defectos. |

## 1. Alcance

OnTimeAI predice demoras de llegada de vuelos que salen de Atlanta (ATL) con un
modelo LightGBM alimentado por un harvester FR24/OpenSky, y las muestra en un
dashboard web y en apps móviles. Son tres repositorios que se despliegan por
separado a Cloud Run y comparten una base SQLite en Google Cloud Storage.

**Se prueba:**

- Backend: la API HTTP (autenticación, vuelos, métricas, cascada, perfil
  viajero), el pipeline de inferencia (`live_pull.py`, `live_job.py`), el
  paquete `ontimeai` (features, calibración, lineage, training store), el
  vigía (`watchdog.py`) y los scripts que corren en producción.
- Scrapper: el ciclo del harvester, la reconciliación de identidades FR24, el
  cierre de outcomes pendientes, el cliente de GCS con *compare-and-swap* por
  generación.
- Frontend: la lógica de dominio en `src/lib`, los handlers de `src/app/api`,
  los componentes con lógica propia, la política de CSP y el proxy.
- Integraciones externas: GCS (contrato con dobles y prueba contra el bucket
  real), FR24 (contrato con dobles y canary contra el servicio real).
- Calidad no funcional: rendimiento bajo carga y esfuerzo sostenido de la API,
  complejidad ciclomática, duplicación, cobertura.

**No se prueba en este plan:** la precisión estadística del modelo (es objeto
de la tesis, se mide con AUC y Brier en `/metrics/model` y en los documentos de
calibración del Backend), el comportamiento de las apps nativas en dispositivos
físicos (sólo se verifica que compilen) y la infraestructura de Google Cloud
en sí.

## 2. Nivel declarado y metas

Se declara **Nivel 2, prototipo parcial**: el sistema corre en producción y en
las tiendas, pero la calibración del modelo, la fase 4 (inferencia desde el
buffer FR24) y las apps siguen en validación, y la cobertura medida al inicio
(52,6 % / 50,7 % / 17,6 % de líneas sobre el código desplegado) no se acerca al 80 % que exige el Nivel 3.

| Meta | Exigido para Nivel 2 | Cómo se cumple | Verificación |
|---|---|---|---|
| Pipeline | compilación, pruebas, análisis estático, cobertura, quality gate, reporte automático | `ci.yml` de cada repo | runs en GitHub Actions |
| Quality gate | bloquea bugs críticos, duplicación > 5 %, cobertura sobre código nuevo < 80 % | `ruff`/ESLint en reglas de error, `jscpd --threshold 5`, `diff-cover --fail-under 80` | paso rojo en el PR |
| Cobertura sobre código nuevo | 80 % | `diff-cover` contra `origin/main` | paso rojo en el PR |
| Cobertura sobre código existente | 60 % | trinquete `fail_under` que sólo sube (al cierre: Backend 58 % combinado, Scrapper 60, Frontend 32/24/20/32; al inicio 50 / 46 / 17-13-10-17); tests de caracterización sobre los módulos sin cobertura. Se mide sobre **el código desplegado**: lo que copian los Dockerfiles. Resultado sobre `main` (sentencias): Backend 61,1 %, Scrapper 64,8 % (2026-10-23), Frontend 39,3 % (2026-10-25); combinada que imprime el CI: Backend 59,0 %, Scrapper 60,7 % | `mediciones/2026-10-22-antes`, `2026-10-23-main` y `2026-10-25-main` |
| Smoke test | ejecutado por el pipeline tras el despliegue | job `smoke` al final de cada `deploy.yml` | run del deploy |
| Integración externa | una probada contra entorno real | GCS con CAS contra bucket de QA | workflow `integration.yml` |
| Stress y esfuerzo sostenido | ejecutado, con resultados y umbrales | k6 en `stress.yml` (stress 3 min, soak 10 min) | artifacts y resumen del run |
| Plan de pruebas y riesgos | versionado, con criterios de entrada y salida, riesgos P × I, trazabilidad | este documento y los enlazados | este repo |
| Defectos | con pasos, esperado y obtenido, vinculados a su caso de prueba | GitHub Issues con el formulario "Defecto" | [DEFECTOS.md](DEFECTOS.md) |
| Herramienta nueva | proceso de cinco pasos | k6 | [HERRAMIENTA_K6.md](HERRAMIENTA_K6.md) |

## 3. Niveles de prueba y dónde corren

| Nivel | Qué verifica | Backend | Scrapper | Frontend | Dónde corre |
|---|---|---|---|---|---|
| Unitario | funciones y módulos aislados, patrón Arrange-Act-Assert | pytest, `tests/test_*.py` | pytest | vitest, `__tests__` | local y CI en cada push y PR |
| Integración | componentes juntos con dobles de lo externo | `TestClient` de FastAPI con bases temporales; dobles de GCS, AeroAPI, IEM | dobles de FR24 y GCS (`test_gcs_generation.py`) | handlers de `app/api` con `fetch` simulado | CI |
| Integración real | contrato contra el servicio externo | — | GCS con CAS contra `ontimeai-prod-qa`; canary FR24 | — | `integration.yml` |
| Sistema | la API completa bajo carga; el build completo | k6 smoke, stress, soak contra la API con base fixture | `validate_sources.py` | `next build`, `build-mobile.mjs` | `stress.yml`, `ci.yml`, `android-build.yml` |
| Aceptación | el despliegue nuevo responde | smoke post-deploy: login + `/metrics/summary` + `/flights` | smoke: imagen desplegada y última ejecución del harvester | smoke: `/` y `/login` responden | `deploy.yml` tras cada merge a `main` |

Despliegue verificado en cada instancia: local (`uvicorn`, `pnpm dev`), CI
(GitHub Actions `ubuntu-latest`, Python 3.11 y Node 20, mismas versiones que
producción), Cloud Run (`deploy.yml` con Workload Identity, sin claves) y
tiendas (Play interno, TestFlight) para las apps.

## 4. Tipos de prueba

| Tipo | Herramienta | Cuándo |
|---|---|---|
| Funcional unitaria y de integración | pytest, vitest | cada push y PR |
| API | `TestClient` (pytest) y k6 smoke | cada PR |
| Regresión | un test por cada defecto corregido (ver [DEFECTOS.md](DEFECTOS.md)) | cada PR |
| Smoke | `curl` contra el servicio desplegado | tras cada deploy |
| Carga, stress y esfuerzo sostenido | k6 | PR (smoke + stress), `main` (más soak) |
| Análisis estático | ruff, ESLint, `tsc`, gate de complejidad, jscpd | cada PR |
| Cobertura de sentencia y de decisión | pytest-cov `--cov-branch`, vitest v8 | cada PR |
| Exploratoria | manual, sobre el dashboard desplegado | antes de cada demo |

## 5. Entornos

| Entorno | Datos | Credenciales | Uso |
|---|---|---|---|
| Local | `live_data.db` bundleada más vuelos sembrados | variables de prueba en `tests/conftest.py` | desarrollo |
| CI | igual que local, base fixture generada por `scripts/make_fixture_db.py` | literales de prueba | gates, stress |
| QA en GCS | bucket `ontimeai-prod-qa`, objetos descartables | Workload Identity del deployer | integración real |
| Producción | `gs://ontimeai-prod-live-db` | secretos del servicio | smoke post-deploy, sólo lectura |

Regla fija: **nada de carga contra producción**. El backend corre en una sola
instancia y comparte CPU con el refresco de la base.

## 6. Criterios de entrada y salida

**Entrada a pruebas de un cambio:** el cambio está en una rama con PR abierto
contra `main`; el PR describe qué hace y cómo se verifica; si corrige un
defecto, el issue existe con pasos, esperado y obtenido, y el PR trae el test
de regresión.

**Salida (el PR puede mergearse):** todos los jobs del CI en verde:

1. tests unitarios y de integración sin fallos;
2. cobertura total no menor al trinquete del repo y cobertura sobre las líneas
   cambiadas ≥ 80 %;
3. sin funciones nuevas con complejidad > 10 y sin crecimiento de las exentas;
4. duplicación ≤ 5 %;
5. sin errores de ruff/ESLint/`tsc`;
6. para cambios en la API, stress en verde con sus umbrales;
7. revisión del PR por otra persona del grupo cuando el cambio toca producción.

**Salida de un despliegue:** el job `smoke` del `deploy.yml` en verde. Si falla,
se revierte con el deploy anterior (`gcloud run services update-traffic`) y se
abre un defecto.

**Suspensión:** se suspende la ejecución si la base fixture no se puede generar
o si una dependencia externa necesaria para el nivel (GCS para la integración
real) no responde; se reanuda cuando el pre-requisito vuelve, sin saltar
niveles.

## 7. Riesgos, trazabilidad y defectos

Los riesgos priorizados por probabilidad × impacto están en
[RIESGOS.md](RIESGOS.md); cada riesgo alto apunta a los casos que lo cubren. La
trazabilidad requisito → caso → defecto está en
[TRAZABILIDAD.md](TRAZABILIDAD.md). Los defectos se registran como issues con el
formulario "Defecto" y se indexan en [DEFECTOS.md](DEFECTOS.md).

## 8. Métricas del plan

| Métrica | Tipo | Fuente | Objetivo |
|---|---|---|---|
| Cobertura de líneas y ramas por repo (código desplegado) | producto | `mediciones/` y artifacts del CI | ≥ 60 % líneas al cierre; no baja nunca |
| Funciones con complejidad > 10 | producto | gate de complejidad | sólo baja |
| Duplicación | producto | jscpd | ≤ 5 % |
| Defectos por módulo | producto | registro de defectos | concentración conocida (`api.py`) |
| Lead time de un PR (apertura → merge) | proceso | `gh pr list` | mediana < 2 días |
| Proporción de fixes con test de regresión | proceso | git log | 100 % |
| Duración del CI | proceso | GitHub Actions | < 10 min |
| Valor ganado del TP (planificado vs. completado) | proyecto | cronograma §9 | SPI ≥ 0,9 |

## 9. Cronograma del TP

| Día | Entregable |
|---|---|
| 2026-10-22 | línea de base medida; gates de complejidad en los tres repos |
| 2026-10-23 | cobertura y quality gate en CI; hub con plan, riesgos, ISO |
| 2026-10-24 | k6 stress y soak; smoke post-deploy; integración GCS real |
| 2026-10-25 | casos CE/VL/TD con tests; registro de defectos; refactor medido |
| 2026-10-26 | informe con los números finales; demo con despliegue nuevo |

## 10. Roles

| Rol | Responsabilidad |
|---|---|
| Autor del cambio | tests unitarios, regresión del defecto que corrige, PR con descripción |
| Revisor | lectura del PR, verificación de criterios de salida, aprobación |
| Responsable de calidad del TP | mantiene este plan, los riesgos, la trazabilidad y las mediciones |
| Operación | reacciona a las alertas del vigía y al smoke post-deploy |
