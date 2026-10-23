# Mejora medida 02: `_upload_create_only` (Backend, `ontimeai/training_store.py`)

Fecha: 2026-10-23. Mismo PR que la mejora 01 (Backend #94). Función de 97
líneas que subía un objeto inmutable al training store y, si ya existía,
verificaba que fuera idéntico por metadatos, SHA-256 y comparación semántica
(Parquet por identidad lógica, JSON por igualdad). Cobertura previa del tramo:
78 %.

## Antes

```
$ ruff check --select C901 --ignore-noqa ontimeai/training_store.py
ontimeai/training_store.py:1132:5: C901 `_upload_create_only` is too complex (11 > 10)
$ radon cc -s ontimeai/training_store.py | grep _upload_create_only
    F 1132:0 _upload_create_only - C (19)
```

## Qué se cambió

- `_parquet_ledger_matches(existing_body, expected_metadata, object_name)`:
  la identidad lógica del Parquet remoto (cantidad, digest de ids, digest de
  hashes); lanza `ValueError` si no coincide.
- `_existing_object_is_identical(blob, body, …)`: metadatos, SHA-256 y la
  comparación semántica por tipo; lanza `RuntimeError` ante cualquier
  diferencia, con los mismos mensajes que antes.
- `_upload_create_only` queda con la subida con `if_generation_match=0` y la
  decisión de verificar ante `PreconditionFailed`.

## Después

```
$ radon cc -s ontimeai/training_store.py | grep -E "_upload_create_only|_existing_object|_parquet_ledger"
    F 1163:0 _existing_object_is_identical - C (11)
    F 1132:0 _parquet_ledger_matches - B (7)
    F 1217:0 _upload_create_only - A (3)
```

| | Antes | Después |
|---|---|---|
| Complejidad (ruff) de `_upload_create_only` | 11 | 3 |
| Complejidad (radon) | C (19) | A (3) |
| Mayor complejidad entre las piezas resultantes (ruff) | 11 | ≤ 10 (ninguna por encima del umbral) |
| Funciones exentas en la baseline del gate | 20 | 19 |
| Tests del training store / suite completa | 51 / 558 verdes | 51 / 558 verdes |
