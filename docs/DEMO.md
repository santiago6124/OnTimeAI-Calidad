# Guion de la demostración (26/10)

Objetivo: mostrar un despliegue nuevo con las integraciones, pruebas y cargas
exigidas, y que las decisiones se apoyan en datos. Dura 15 minutos. Todo lo
que se muestra es un run real de GitHub Actions o un archivo de este repo.

## Antes de la demo

Los 16 PRs del TP ya están mergeados en `main` de los tres repos (2026-10-23),
los trinquetes subidos al valor real y la medición definitiva en
`mediciones/2026-10-23-main`. Para la demo sólo hace falta tener abiertas las
pestañas: Actions de los tres repos, `docs/EVIDENCIA_CI.md`,
`mediciones/2026-10-22-antes/resumen.md` y `mediciones/2026-10-23-main/resumen.md`.
Si algún merge nuevo entra antes del 26, repetir `scripts/medir.py` y `informe/build.sh`.

## Minuto a minuto

| Min | Qué se muestra | Dónde |
|---|---|---|
| 0 | Antes de empezar a hablar, lanzar el despliegue y las cargas: `gh workflow run deploy.yml --repo santiago6124/OnTimeAI-Backend --ref main` (el smoke corre solo cuando termina), `gh workflow run stress.yml --repo santiago6124/OnTimeAI-Backend --ref main` y `gh workflow run integration.yml --repo santiago6124/OnTimeAI-Scrapper --ref main` | terminal |
| 0-2 | El nivel declarado y la línea de base del 22/10: cobertura, complejidad, tests | `docs/PLAN_DE_PRUEBAS.md` §2, `mediciones/2026-10-22-antes/resumen.md` |
| 2-5 | Un PR nuevo en vivo: la rama `demo/gate-en-vivo` ya tiene un commit con `ontimeai/demo_calidad.py` (complejidad 11). Abrir el PR en vivo con `gh pr create --repo santiago6124/OnTimeAI-Backend --head demo/gate-en-vivo --base main --title "demo: gate en vivo" --body "no mergear"`; el CI falla en "Complejidad ciclomática" con `clasificar_demora_para_la_demo CC=11`. Después `git revert HEAD`, push, y verde. Cerrar el PR sin mergear | Backend |
| 5-7 | El run rojo que detectó un problema real: `F821` en `adsb_lineage.py`, el issue #90 con pasos, esperado y obtenido, y el test que falla en el commit padre | `docs/EVIDENCIA_CI.md`, issue #90, `mediciones/evidencia/DEF-01-*.txt` |
| 7-9 | Despliegue nuevo: el `Deploy` lanzado al minuto 0 (tarda ~12 min, así que se muestra en curso) y, como respaldo, el último `Deploy` completo con el `Smoke` que lo siguió, siete checks contra Cloud Run. Volver a la pestaña al minuto 14 para ver el smoke del despliegue nuevo | Actions del Backend |
| 9-11 | Stress y soak: el run de `stress.yml` lanzado al minuto 0 (en curso; el soak dura 10 min) y el último completo como respaldo, el resumen con p95 y tasa de error por escenario, los umbrales en el script | Actions del Backend, `k6/` |
| 11-12 | Integración real: el run de `integration.yml` lanzado al minuto 0 (dura menos de un minuto) contra `ontimeai-prod-qa`, los seis pasos del contrato CAS | Actions del Scrapper |
| 12-14 | Antes y después: la tabla de `mediciones/`, el refactor de 16 a 5, la baseline de 21 a 18, el riesgo RP-08 | `mediciones/evidencia/MEJORA-01-*.md`, `docs/RIESGOS.md` |
| 14-15 | Lo que no se cumplió y por qué (cobertura 60 % en Frontend), y lo que sigue | informe, sección de metas no cumplidas |

## Preguntas individuales probables

- ¿Por qué el umbral de complejidad es 10 y no 15? (McCabe clásico; la clase
  del 31/08; con 15 quedaban 10 exentas en vez de 21 pero sin cambiar la
  práctica.)
- ¿Qué diferencia hay entre ruff y radon en la medición? (operadores
  booleanos y clases; `live_pull.py:main` 72 contra 157.)
- ¿Qué es un trinquete y cómo se evita que alguien agregue `noqa`?
  (`--ignore-noqa` y comparación contra la baseline.)
- ¿Por qué no se hace stress contra producción? (una instancia, PR #26.)
- ¿Qué garantiza el CAS y qué pasó el 2026-06-08? (`docs/CONTINGENCIA.md`.)
- ¿Cómo sabemos que la cobertura del informe es la del pipeline?
  (`scripts/medir.py` usa el mismo `source` que `pyproject.toml`.)

## Cierre hecho el 2026-10-23

1. Scrapper: `fail_under` subido de 46 a 60 (PR #24; 60,7 % combinado en `main`).
2. Frontend: `thresholds` en 32/24/20/32 desde el PR #80.
3. Backend: `fail_under` subido de 50 a 59 (PR #101) y dejado en 58 con un punto de margen (PR #102; 59,0 % combinado en `main`).
4. Medición definitiva en `mediciones/2026-10-23-main`; el informe y el PDF usan esos números.
