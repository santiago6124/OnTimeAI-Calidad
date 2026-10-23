# Mejora medida 01: `_coerce_parquet_frame` (Backend, `ontimeai/training_store.py`)

Fecha: 2026-10-23. PR Backend `feat/refactor-complejidad-medido`.
Elegida porque combina complejidad alta (16, exenta en la baseline del gate)
con buena cobertura previa (`training_store.py` al 81 %, 51 tests entre
`test_training_store.py` y `test_materialize_live_training.py`): se puede
refactorizar con red de seguridad. No se eligió `live_pull.py:main` (72) ni
`faa_nas.py:_parse_nas_xml` (27) justamente por lo contrario: 6 % y 0 % de
cobertura. A esas primero hay que escribirles tests de caracterización.

## Antes (medido con las herramientas del gate)

```
$ ruff check --select C901 --ignore-noqa ontimeai/training_store.py
ontimeai/training_store.py:1070:5: C901 `_coerce_parquet_frame` is too complex (16 > 10)

$ radon cc -s ontimeai/training_store.py | grep _coerce_parquet_frame
    F 1070:0 _coerce_parquet_frame - C (18)
```

Una función de 47 líneas con la lectura de dos listas JSON, un bucle con
tres prefijos y una cascada de seis `if`/`elif` para el dtype.

## Qué se cambió

- `_feature_name(col)`: detecta el prefijo `raw__` / `model__` / `imputed__`.
- `_first_json_list(frame, column)`: la lista JSON de la primera fila no nula.
- `_coerce_column(series, col, categorical)`: la cascada de dtypes, una
  decisión por línea, que devuelve la serie intacta si la columna es
  desconocida.
- `_coerce_parquet_frame` queda con el bucle y la verificación del esquema.

## Después

```
$ ruff check --select C901 --ignore-noqa ontimeai/training_store.py
(sin hallazgos)

$ radon cc -s ontimeai/training_store.py | grep -E "_coerce|_feature_name|_first_json"
    F 1091:0 _coerce_column - B (8)
    F 1111:0 _coerce_parquet_frame - A (5)
    F 1073:0 _feature_name - A (3)
    F 1081:0 _first_json_list - A (3)
```

| | Antes | Después |
|---|---|---|
| Complejidad (ruff) de `_coerce_parquet_frame` | 16 | 5 |
| Complejidad (radon) | C (18) | A (5) |
| Mayor complejidad entre las piezas resultantes | 16 | 8 |
| Funciones exentas en la baseline del gate | 21 | 20 |
| Tests del training store | 51 verdes | 51 verdes |
| Comportamiento | — | sin cambios (mismos dtypes, misma excepción ante features faltantes) |

El gate garantiza que no vuelva: `--actualizar-baseline` sólo acepta listas
más chicas, y una función nueva por encima de 10 falla el CI.
