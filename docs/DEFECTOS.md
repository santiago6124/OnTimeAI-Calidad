# Registro de defectos

Cada defecto vive como issue en el repo donde ocurrió, cargado con el
formulario "Defecto" (`.github/ISSUE_TEMPLATE/defecto.yml`): severidad,
entorno, requisito, caso de prueba, pasos, esperado, obtenido y evidencia. Este
archivo es el índice con trazabilidad al requisito, al caso y al PR con su
test de regresión. Los DEF-02 a DEF-10 se registran **retroactivamente** desde
los PRs que los corrigieron (el proyecto venía corrigiendo con test de
regresión desde septiembre pero sin issue formal); los datos salen de la
descripción de cada PR, que ya traía reproducción, causa y medición.

| ID | Fecha | Repo | Severidad | Resumen | Requisito | Caso | Corrección y test de regresión |
|---|---|---|---|---|---|---|---|
| DEF-01 | 2026-10-23 | Backend | alta | el setup de `adsb_lineage` llama a una función que no existe | RNF-05 | CP-EST-01, CP-FE-01 | [#90](https://github.com/santiago6124/OnTimeAI-Backend/issues/90) → PR #91, `tests/test_adsb_lineage.py` |
| DEF-02 | 2026-10-16 | Backend | alta | el calibrador ajustaba sobre el 1,3 % de los datos | RF-01 | CP-CAL-01 | PR #86, `tests/test_chain_calibration.py` |
| DEF-03 | 2026-10-03 | Backend | alta | guardar un vuelo devolvía 200 y leerlos devolvía 500 | RF-06 | CP-API-09 | PR #81, `tests/test_modo_viajero.py` |
| DEF-04 | 2026-09-25 | Backend | crítica | el cache de clima daba todo por fresco y congeló el METAR | RF-01 | CP-LIVE-02 | PR #74, `tests/test_clima_fresco.py` |
| DEF-05 | 2026-09-16 | Backend | alta | `stable_id` colapsaba instancias distintas del mismo vuelo | RF-02 | CP-LIVE-01 | PR #65 (issue #64), `tests/test_stable_id.py` |
| DEF-06 | 2026-09-15 | Backend | crítica | `threshold_used` no salía de la subconsulta y tumbaba `/flights` y `/metrics/summary` | RF-01, RF-05 | CP-API-01 | PR #43, `tests/test_optional_prediction_columns.py` |
| DEF-07 | 2026-09-15 | Backend | media | la ventana activa retenía vuelos que ya aterrizaron | RF-05 | CP-API-05 | PR #52 (issue #51), `tests/test_ventana_activa.py` |
| DEF-08 | 2026-10-19 | Scrapper | alta | el horizonte de 6 h tiraba el 90 % del itinerario ya descargado | RF-07 | CP-SCR-02 | PR #18, `tests/test_future_legs.py` |
| DEF-09 | 2026-10-21 | Frontend | baja | el barrido de "reducir movimiento" apagaba la cortina entera | RNF-06 | CP-UI-01 | PR #71 (sin test automatizado: CSS; verificación manual) |
| DEF-10 | 2026-10-22 | Frontend | alta | el bundle iOS no compilaba desde el PR #55 y no cubría el perfil Viajero | RNF-04 | CP-MOB-01 | PR #73, `build-mobile.mjs --strict` sumado a `ci.yml` |
| DEF-11 | 2026-10-23 | Backend | media | el CLI `predict.py` no puede puntuar vuelos sin historial (`pd.NA` en dtype `object`) | RF-01 | CP-COB-02 | [#97](https://github.com/santiago6124/OnTimeAI-Backend/issues/97); caracterizado en PR #96, pendiente de fix |
| DEF-12 | 2026-10-23 | Backend | baja | el parser de `faa_nas` no lee los minutos anidados del feed real; el módulo no se usa en producción | RF-01 | CP-COB-01 | [#98](https://github.com/santiago6124/OnTimeAI-Backend/issues/98); caracterizado en PR #96, decisión pendiente |

## Fichas

### DEF-01 · bug(adsb): el setup de adsb_lineage llama a una función que no existe

- **Entorno:** CI. **Detectado por:** el gate "Bugs críticos" (ruff F821) del PR #91, primer run rojo.
- **Pasos:** `python -m feature_engineering_v7.adsb_lineage --setup`.
- **Esperado:** descarga la base de aeronaves, construye el mapa `TAIL_NUM → ICAO24` y sale con "Setup completo".
- **Obtenido:** `NameError: name 'download_faa_registry' is not defined` (línea 367).
- **Causa raíz:** el módulo nació en `274b7af` con la descarga llamada `download_aircraft_db`; `main()` conservó el nombre de un borrador. Nadie volvió a correr `--setup` y ningún test pasaba por `main()`.
- **Rojo/verde:** `mediciones/evidencia/DEF-01-adsb-lineage-rojo-verde.txt`: el test falla en el commit padre con `NameError` y pasa con el fix.

### DEF-02 · el calibrador ajustaba sobre el 1,3 % de los datos

- **Entorno:** producción. **Pasos:** medir el ratio tasa real / probabilidad media por día sobre 14 días (12.569 vuelos).
- **Esperado:** ratio cercano a 1 en días buenos y malos.
- **Obtenido:** el modelo subestimaba 1,7× a 2× todos los días (ratio 2,62 el 04/10); el calibrador post-cadena se ajustaba sólo sobre el 1,3 % de las filas.
- **Causa raíz:** el filtro de filas elegibles para recalibrar dejaba afuera casi todo el lote. Corregido en PR #86 con test sobre la distribución.

### DEF-03 · guardar un vuelo devolvía 200 y leerlos devolvía 500

- **Entorno:** producción. **Pasos:** `POST /users/me/flights` con un vuelo válido; luego `GET /users/me/flights`.
- **Esperado:** 200 con la lista que incluye el vuelo guardado.
- **Obtenido:** `Internal Server Error`; `IndexError: No item with that key` en `_flight_row_to_dict` por la columna `has_actual`.
- **Causa raíz:** una consulta a medida (`f.*` más columnas sueltas) alimentaba un helper que lee una lista fija de nombres; `has_actual` es calculada en la consulta canónica y faltaba. PR #81 usa exactamente las columnas de la canónica; `tests/test_modo_viajero.py`.

### DEF-04 · el cache de clima daba todo por fresco y congeló el METAR

- **Entorno:** producción. **Pasos:** correr el ciclo de `live_pull` con observaciones de más de 3 h en la tabla de clima.
- **Esperado:** se vuelven a pedir las estaciones con observación vieja.
- **Obtenido:** 138 de 148 estaciones dadas por frescas, 0 frescas de verdad; el clima dejó de pedirse.
- **Causa raíz:** comparación de fechas como texto: `2026-09-25T14:56:00` (con `T`) contra `datetime('now')` (con espacio); la `T` gana al espacio en la posición 11. Introducido por el propio equipo en #70. PR #74, `tests/test_clima_fresco.py`. Severidad crítica: sin clima, el modelo pierde sus features más importantes.

### DEF-05 · `stable_id` colapsaba instancias distintas del mismo vuelo

- **Entorno:** producción. Reportado en el issue #64.
- **Pasos:** pedir `/flight-history/SYN-DL2595-ATL-BOS-2026-09-16`.
- **Esperado:** el historial de ese vuelo de ese día.
- **Obtenido:** un mes de ciclos de todas las corridas diarias de DL2595, porque `stable_id` recortaba a `SYN-DL2595`.
- **Causa raíz:** el recorte del sufijo de AeroAPI se hacía por "al menos dos segmentos" en vez de por la forma real del sufijo. PR #65, `tests/test_stable_id.py` (ejemplo AAA en [PRINCIPIOS.md](PRINCIPIOS.md)).

### DEF-06 · `threshold_used` no salía de la subconsulta

- **Entorno:** producción, tras el deploy de #40. **Pasos:** `GET /metrics/summary` o `GET /flights`.
- **Esperado:** 200. **Obtenido:** 500, `sqlite3.OperationalError: no such column: p.threshold_used`.
- **Causa raíz:** `p` era una subconsulta derivada que no exponía la columna nueva. Hotfix PR #43 con rollback de tráfico a la revisión anterior mientras tanto; `tests/test_optional_prediction_columns.py`. Este incidente es el origen del smoke post-deploy del TP.

### DEF-07 · la ventana activa retenía vuelos que ya aterrizaron

- **Entorno:** producción. **Pasos:** listar la ventana activa con FR24 como fuente.
- **Esperado:** sólo vuelos en el rango temporal o que todavía no salieron.
- **Obtenido:** 492 de 637 vuelos (77 %) con salida programada hace más de 6 h.
- **Causa raíz:** la condición usaba `actual_out_utc IS NULL`, que AeroAPI poblaba y FR24 nunca (no expone gate-out). PR #52, `tests/test_ventana_activa.py`.

### DEF-08 · el horizonte de 6 h tiraba el 90 % del itinerario ya descargado

- **Entorno:** producción (Scrapper). **Pasos:** chain-walk por matrícula con FR24; contar piernas futuras conservadas.
- **Esperado:** conservar las piernas que llegan en la misma respuesta.
- **Obtenido:** 1 de 12, 1 de 16, 2 de 14: 86-94 % descartado por `FUTURE_LEG_HORIZON_HOURS=6`.
- **Causa raíz:** el horizonte se aplicaba a datos ya pagados en la misma llamada. PR #18, `tests/test_future_legs.py`.

### DEF-09 · el barrido de "reducir movimiento" apagaba la cortina entera

- **Entorno:** navegador con `prefers-reduced-motion`. **Pasos:** abrir la vista de meteorología con la preferencia activa.
- **Esperado:** nubes quietas pero visibles. **Obtenido:** cortina invisible.
- **Causa raíz:** regla global en `globals.css` con `!important` sobre los longhands de animación que anulaba la regla del componente. PR #71. Sin test automatizado: es CSS y la verificación fue manual (queda como caso exploratorio CP-UI-01).

### DEF-10 · el bundle iOS no compilaba desde #55 y no cubría el perfil Viajero

- **Entorno:** CI y app iOS. **Pasos:** `node scripts/build-mobile.mjs --strict`.
- **Esperado:** bundle estático compilado con las páginas del perfil Viajero.
- **Obtenido:** `TS2307: Cannot find module '@/lib/server-auth'`; tres semanas de merges en verde porque `ci.yml` no compilaba el bundle.
- **Causa raíz:** el script poda `server-auth.ts` pero `server-profile.ts` lo importaba; el typecheck de `next build` lo revisa aunque ninguna página lo alcance. PR #73 suma el build móvil al CI (regresión estructural) y publica el OTA 1.0.3.

### DEF-11 · el CLI predict.py no puede puntuar vuelos sin historial

- **Entorno:** local. **Detectado por:** tests de caracterización de `predict.py` (PR #96).
- **Pasos:** CSV de vuelos futuros sin `ARR_DELAY` ni eventos UTC; `python predict.py …`.
- **Esperado:** puntúa imputando las features de linaje con el fallback cold-deck.
- **Obtenido:** `ValueError: pandas dtypes must be int, float or bool` (features creadas con `pd.NA` en `object`).
- **Alcance:** el pipeline live no pasa por ese camino; producción no está afectada. Test con `pytest.raises` listo para el contraste rojo/verde del fix.

### DEF-12 · el parser de faa_nas no lee los minutos anidados y el módulo es código muerto

- **Entorno:** local. **Detectado por:** tests de caracterización de `ontimeai/faa_nas.py` (PR #96, que lo llevó de 0 a 100 % de cobertura).
- **Pasos:** parsear el XML real del feed de la FAA (`Min`/`Max` anidados en `Arrival_Departure`).
- **Esperado:** banderas, motivo y minutos. **Obtenido:** banderas y motivo sin minutos.
- **Causa raíz:** el parser busca `Min`/`Max` como hijos directos; además ningún módulo productivo importa `faa_nas` (`live.py` usa `GdpClient`). Decisión pendiente: corregir y conectar, o retirar de la imagen.

## Lo que muestra el registro

- Nueve de los diez primeros tienen test de regresión en el mismo PR; el único sin
  test es CSS (DEF-09). DEF-11 y DEF-12 aparecieron al escribir tests de
  caracterización para subir la cobertura: los tests encontraron defectos en código
  que llevaba meses sin ejecutarse.
- Cinco de diez vivieron en producción (DEF-02, 03, 04, 06, 07) y dos de esos
  se introdujeron en PRs propios (#70 → DEF-04, #40 → DEF-06): el argumento
  para el smoke post-deploy y para el gate de cobertura sobre código nuevo.
- Tres tienen la misma forma: una suposición válida con AeroAPI que FR24 no
  cumple (DEF-05, DEF-07, y el `departure_delay_min` del Scrapper). Es el
  riesgo RP-11 de [RIESGOS.md](RIESGOS.md).
