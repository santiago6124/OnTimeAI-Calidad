# Mejora medida 03: `apply_lineage_fallback` (Backend, `ontimeai/lineage_fallback.py`)

Fecha: 2026-10-23. PR Backend #94. La más compleja de las tres refactorizadas:
una función de 120 líneas que imputaba, con el mismo patrón repetido cinco
veces, los NaN de las features de linaje (demora del tramo anterior,
turnaround, tasas de demora por aerolínea, origen y destino), más los valores
neutros de las features ADS-B. Cobertura previa del tramo: 93 %
(`tests/test_lineage_fallback.py`, 10 tests).

## Antes

```
$ ruff check --select C901 --ignore-noqa ontimeai/lineage_fallback.py
ontimeai/lineage_fallback.py:155:5: C901 `apply_lineage_fallback` is too complex (23 > 10)
$ radon cc -s ontimeai/lineage_fallback.py | grep apply_lineage_fallback
    F 155:0 apply_lineage_fallback - D (26)
```

## Qué se cambió

- `_scheduled_hour(out)`: la hora programada desde `CRS_DEP_MIN` o `CRS_DEP_TIME`.
- `_fill_columns(out, cols, layers, default)`: el patrón repetido, una sola
  vez: lookup jerárquico y `fillna` sobre las columnas presentes.
- `_fill_adsb_defaults(out)`: los valores neutros de las features ADS-B y el
  proxy de tiempos de bloque.
- `apply_lineage_fallback` queda como la lista de qué se imputa con qué capas.

Mismos lookups, mismo orden de capas, mismos valores por defecto.

## Después

```
$ radon cc -s ontimeai/lineage_fallback.py | grep -E "apply_lineage|_fill_|_scheduled"
    F 251:0 _fill_adsb_defaults - B (7)
    F 170:0 _fill_columns - A (5)
    F 180:0 apply_lineage_fallback - A (4)
    F 161:0 _scheduled_hour - A (3)
```

| | Antes | Después |
|---|---|---|
| Complejidad (ruff) de `apply_lineage_fallback` | 23 | 4 |
| Complejidad (radon) | D (26) | A (4) |
| Mayor complejidad entre las piezas resultantes (radon) | 26 | 7 |
| Funciones exentas en la baseline del gate | 19 | 18 |
| Tests del módulo / suite completa | 10 / 558 verdes | 10 / 558 verdes |

## Lo que mostró el proceso

En el primer intento el reemplazo dejó afuera el final de la función (el
bloque ADS-B y el `return out`): los 10 tests de lineage fallaron en el acto,
siete de ellos con `None` en vez de un DataFrame. Es exactamente el caso de
uso de la red de tests antes de refactorizar, y la razón por la que no se tocó
`live_pull.py:main` (6 % de cobertura).

## Las tres mejoras juntas

| Función | ruff antes → después | radon antes → después |
|---|---|---|
| `_coerce_parquet_frame` | 16 → 5 | C (18) → A (5) |
| `_upload_create_only` | 11 → 3 | C (19) → A (3) |
| `apply_lineage_fallback` | 23 → 4 | D (26) → A (4) |
| Baseline del gate | 21 exentas | **18 exentas** |
