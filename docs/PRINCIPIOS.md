# Los siete principios del testing, aplicados a OnTimeAI

| # | Principio | Cómo se ve en el proyecto | Evidencia |
|---|---|---|---|
| 1 | Las pruebas muestran la presencia de defectos, no su ausencia | 544 tests verdes en el Backend no evitaron que la cadena de ajustes rompiera la calibración durante semanas: cada test verificaba su pieza, ninguno la distribución resultante. | Brier 0,133 → 0,195 (AGENTS.md, 2026-09-06); corregido en #59 y #86 con un test que mira la distribución |
| 2 | Las pruebas exhaustivas son imposibles | La API tiene 33 endpoints con filtros, fechas y perfiles; el modelo 84 features. Se prueban clases de equivalencia y valores límite, no cada combinación. | [CASOS_DE_PRUEBA.md](CASOS_DE_PRUEBA.md): bandas de riesgo en el umbral ± 1, gracia de outcomes en 29/30/31 min |
| 3 | Pruebas tempranas | El CI corre en cada push y PR desde septiembre; el gate de complejidad corre antes que la suite porque tarda segundos. | `ci.yml` de los tres repos; run rojo del gate antes de mergear |
| 4 | Agrupamiento de defectos | 19 de los 45 fixes desde agosto cayeron en `api.py`; 6 en `ontimeai/live.py`; 5 en `live_pull.py`. Tres archivos concentran dos tercios de los defectos. | `git log --grep '^fix' --name-only` sobre `origin/main`; tabla en `mediciones/2026-10-22-antes` |
| 5 | Paradoja del pesticida | Los tests de `test_api.py` se saltaban cuando la base no tenía vuelos "de hoy": pasaban sin verificar nada. Se sembró un vuelo de hoy y empezaron a detectar regresiones de esquema. | fixture `_sembrar_vuelo_de_hoy` (PR #58); los casos nuevos del TP salen de incidentes reales, no de los tests viejos |
| 6 | Las pruebas dependen del contexto | El modelo se evalúa con AUC y Brier sobre ventanas móviles; la API con `TestClient` y k6; el harvester con dobles de FR24 y una prueba real de GCS; las apps con un build estricto. | `test_evaluation.py`, `test_api.py`, `stress.yml`, `test_gcs_generation.py`, `build-mobile.mjs --strict` |
| 7 | Falacia de la ausencia de errores | Un sistema sin bugs que marca el 46,6 % de los vuelos como demorados cuando debería marcar el 22 % no sirve: la precisión era 0,245 con 59.395 falsos positivos. La calidad se define por el objetivo del usuario, no por el verde del CI. | `estimated_dep_delay_adjust` con pisos hardcodeados (AGENTS.md); objetivos OU-01 y OU-02 |

## Arrange, Act, Assert y el criterio de aceptación antes de ejecutar

Los tests del proyecto siguen el patrón de tres bloques. Ejemplo real
(`tests/test_stable_id.py`, Backend):

```python
def test_dos_instancias_del_mismo_vuelo_no_colapsan():
    # Arrange: dos filas del mismo número de vuelo, misma ruta, fechas distintas
    hoy = _fila("DL123", "ATL", "MIA", "2026-10-01T12:00:00Z")
    manana = _fila("DL123", "ATL", "MIA", "2026-10-02T12:00:00Z")
    # Act
    a, b = stable_id(hoy), stable_id(manana)
    # Assert: criterio fijado en el issue antes de escribir el fix (#65)
    assert a != b
```

El criterio de aceptación se fija antes de ejecutar: el formulario de defecto
exige "resultado esperado" y el PR trae el test rojo primero (ver
[DEFECTOS.md](DEFECTOS.md), contraste rojo/verde).
