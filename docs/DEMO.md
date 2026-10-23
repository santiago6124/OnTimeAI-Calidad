# Guion de la demostración (26/10)

Objetivo: mostrar un despliegue nuevo con las integraciones, pruebas y cargas
exigidas, y que las decisiones se apoyan en datos. Dura 15 minutos. Todo lo
que se muestra es un run real de GitHub Actions o un archivo de este repo.

## Antes de la demo

1. Mergear los PRs en este orden (cada merge a `main` del Backend despliega a
   Cloud Run y dispara el smoke):
   - Backend: #89 (gate) → #91 (cobertura y quality gate) → `refactor` → #93 (casos) → #92 (smoke) → `stress-k6`.
   - Scrapper: #19 (gate) → #20 (cobertura y quality gate) → #21 (valores límite) → `integracion-gcs-real`.
   - Frontend: #74 (gate) → cobertura y quality gate.
2. Correr `python scripts/medir.py <repo> --carpeta 2026-10-26-despues` para
   los tres repos y `python scripts/metricas_proceso.py`.
3. Tener abiertas las pestañas: Actions de los tres repos, `docs/EVIDENCIA_CI.md`,
   `mediciones/2026-10-22-antes/resumen.md` y la carpeta `despues`.

## Minuto a minuto

| Min | Qué se muestra | Dónde |
|---|---|---|
| 0-2 | El nivel declarado y la línea de base del 22/10: cobertura, complejidad, tests | `docs/PLAN_DE_PRUEBAS.md` §2, `mediciones/2026-10-22-antes/resumen.md` |
| 2-5 | Un PR nuevo en vivo: agregar una función con complejidad 12 a `api.py`, push, y el CI en rojo en "Complejidad ciclomática" con el nombre de la función. Después revertir y verde | Backend, rama `demo/gate-en-vivo` |
| 5-7 | El run rojo que detectó un problema real: `F821` en `adsb_lineage.py`, el issue #90 con pasos, esperado y obtenido, y el test que falla en el commit padre | `docs/EVIDENCIA_CI.md`, issue #90, `mediciones/evidencia/DEF-01-*.txt` |
| 7-9 | Despliegue nuevo: el run de `Deploy` del último merge y el `Smoke` que lo siguió, siete checks contra Cloud Run | Actions del Backend |
| 9-11 | Stress y soak: el run de `stress.yml`, el resumen con p95 y tasa de error por escenario, los umbrales en el script | Actions del Backend, `k6/` |
| 11-12 | Integración real: el run de `integration.yml` contra `ontimeai-prod-qa`, los seis pasos del contrato CAS | Actions del Scrapper |
| 12-14 | Antes y después: la tabla de `mediciones/`, el refactor de 16 a 5, la baseline de 21 a 20, el riesgo RP-08 | `mediciones/evidencia/MEJORA-01-*.md`, `docs/RIESGOS.md` |
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
