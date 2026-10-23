# Herramienta incorporada: k6, con el proceso de cinco pasos

La materia (clase del 28/09) pide incorporar una herramienta nueva siguiendo
requisitos → mercado → prueba de concepto → evaluación objetiva → despliegue
incremental. OnTimeAI no tenía ninguna prueba de carga; la elegida fue **k6**.
Los números de la PoC salen del PR del Backend `feat/stress-k6` y de sus runs.

## Paso 1: requisitos

| Pregunta de la cátedra | Respuesta para OnTimeAI |
|---|---|
| ¿Qué problema concreto queremos resolver? | Nadie sabe cuántos usuarios concurrentes aguanta la API ni cómo se degrada con el tiempo. El backend corre en **una sola instancia** (PR #26) y comparte CPU con el refresco de la base: un pico de uso del dashboard puede demorar el ciclo de predicción. Hace falta medir latencia y errores bajo carga y bajo esfuerzo sostenido, con umbrales que corten el CI. |
| ¿Quién la va a usar y con qué frecuencia? | El pipeline, en cada PR que toque la API (smoke + stress) y en cada merge a `main` (más soak). Las personas sólo leen el resumen. |
| ¿Con qué tiene que integrarse? | GitHub Actions (runner `ubuntu-latest` sin GUI), la API levantada en el propio runner con una base fixture, umbrales como código versionado, reporte en el resumen del job y como artifact. |
| ¿Qué presupuesto y plazo? | Costo cero (repos públicos), cuatro días de TP, sin servidores propios. |
| ¿Qué pasa si no la implementamos? | Se sigue sin saber el punto de quiebre de la API; la primera señal de un problema de capacidad sería un incidente en producción, como ya pasó con la base (RP-02) y el calibrador (RP-03). |

Requisitos de corte: (R1) corre sin GUI en CI; (R2) umbrales declarativos que
devuelven código de salida distinto de cero; (R3) escenarios de rampa y de
duración fija; (R4) resultados exportables (JSON) para el informe; (R5) sin
costo ni cuenta externa; (R6) curva de aprendizaje compatible con un equipo
que ya escribe JavaScript (Frontend) y Python (Backend).

## Paso 2: investigación de mercado

Shortlist de cuatro, todas open source y usadas en la industria:

| Candidata | Modelo | Lenguaje de los scripts | Umbrales como código | CI sin GUI | Reporte |
|---|---|---|---|---|---|
| **k6** (Grafana) | binario Go, un solo ejecutable | JavaScript (ES6) | sí, `thresholds` en el script; sale con código 99 si fallan | sí, acción oficial `grafana/setup-k6-action` | JSON, texto, `handleSummary` |
| **Locust** | Python, proceso con workers | Python | no nativo: hay que leer stats y fallar a mano, o usar plugins | sí (`--headless`) | CSV, HTML |
| **JMeter** (Apache) | Java, GUI y modo consola | XML (`.jmx`) generado desde la GUI | parcial: aserciones por request, no SLO globales sin plugins | sí (`-n`), pero necesita JVM | JTL, HTML |
| **Artillery** | Node | YAML más JS | sí (`ensure`) | sí | JSON, HTML |

Descartes tempranos: JMeter por la JVM y por scripts XML que no se revisan en
un PR; Gatling por la misma razón (Scala). BlazeMeter y k6 Cloud por costo.

## Paso 3: prueba de concepto

Alcance acotado, como pide la cátedra: un repo (Backend), tres escenarios
(smoke, stress, soak), contra la API levantada localmente con una base fixture
sembrada con vuelos de hoy (`scripts/make_fixture_db.py`), y después el mismo
flujo en el runner de GitHub Actions.

Criterios de éxito definidos antes de correr:

1. los tres escenarios corren sin intervención y producen un JSON por escenario;
2. un umbral violado hace fallar el job (código de salida distinto de 0);
3. el resumen del job muestra VUs, iteraciones, RPS, p50/p95/p99 y tasa de error;
4. el tiempo total en CI es menor a 20 minutos;
5. no se toca producción.

Resultados: ver la sección "PoC medida" al final (se completa con los runs del
PR `feat/stress-k6`).

## Paso 4: evaluación objetiva (matriz de decisión)

Pesos según los requisitos del paso 1. Puntaje de 1 a 10.

| Criterio | Peso | k6 | Locust | JMeter | Artillery |
|---|---|---|---|---|---|
| Funcionalidad: rampas, soak, umbrales, tags por endpoint (R2, R3) | 30 % | 9 | 6 | 7 | 8 |
| Integración con CI y reporte (R1, R4) | 25 % | 9 | 6 | 5 | 8 |
| Costo total (R5): licencias, infraestructura, mantenimiento | 20 % | 10 | 9 | 7 | 9 |
| Facilidad de uso y curva de aprendizaje (R6) | 15 % | 8 | 9 | 4 | 7 |
| Comunidad, documentación y soporte | 10 % | 9 | 7 | 9 | 6 |
| **Total ponderado** | | **9,1** | 7,2 | 6,3 | 7,9 |

Lectura: Locust habría sido la opción más cómoda para el equipo de Python, pero
pierde en lo que más pesa, los umbrales como código y el reporte en CI. k6
gana por R2 y R4; Artillery queda segunda y es la alternativa si el equipo
prefiere YAML.

## Paso 5: despliegue incremental

1. **Piloto:** Backend, tres escenarios, en PR y en `main`, sin bloquear
   todavía ningún merge ajeno al stress (el workflow es independiente de
   `ci.yml`).
2. **Expansión:** sumar el endpoint de cascada y las rutas del perfil Viajero
   al mix; correr el soak sólo en `main` y de noche si el tiempo del runner
   molesta.
3. **Organización:** una corrida mensual contra una revisión etiquetada de
   Cloud Run sin tráfico (`--tag qa --no-traffic`) para tener números de
   infraestructura real; umbrales por entorno.

En cualquier paso se vuelve atrás: si los umbrales no se sostienen en el
runner, se ajustan documentando el motivo antes de seguir.

## PoC medida

PR Backend #95 (`feat/stress-k6`): scripts en `k6/`, workflow `stress.yml`,
`scripts/make_fixture_db.py` (200 vuelos de hoy sembrados, reproducible por
semilla), `docs/STRESS_K6.md`. Un proceso de `uvicorn`, como el `CMD` del
Dockerfile; cada VU hace login una vez y repite el mix de un usuario del
dashboard (nueve requests) con un segundo de pausa.

Local (2026-10-23, Mac, k6 v2.3.0, soak acortado a 3 min para la PoC):

| Escenario | VUs máx | Iteraciones | req/s | p50 | p95 | p99 | Errores HTTP | Checks | Umbrales |
|---|---|---|---|---|---|---|---|---|---|
| smoke | 1 | 20 | 5,8 | 37 ms | 135 ms | 325 ms | 0 % | 100 % | OK (2/2) |
| stress | 50 | 142 | 7,1 | 1,7 s | 11,1 s | 12,6 s | 0 % | 100 % | OK (3/3) |
| soak | 20 | 163 | 6,7 | 2,1 s | 6,8 s | 10,7 s | 0 % | 100 % | OK (3/3) |

Criterios de éxito del paso 3: (1) tres escenarios con JSON por escenario
(`k6/resultados/`): sí; (2) un umbral violado falla el job (exit 99): sí,
probado con el trinquete de thresholds del script; (3) resumen con VUs,
iteraciones, RPS, p50/p95/p99 y tasa de error: sí, `scripts/k6_resumen.py` en
el step summary; (4) menos de 20 minutos en CI: sí (smoke + stress en el PR;
soak de 10 min sólo en `main` y a mano); (5) producción intacta: sí.

Runs en CI: [40011348475](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40011348475)
(PR, smoke + stress, verde) y [40011382323](https://github.com/santiago6124/OnTimeAI-Backend/actions/runs/40011382323)
(a mano desde la rama, con soak de 10 min).

Umbrales finales: `http_req_failed < 1 %` y `checks > 99 %` en los tres;
p95 de `http_req_duration` < 30 s en stress y < 35 s en soak, ≈ 2× la peor
medición local, porque los runners son más lentos y dos corridas iguales
difirieron bastante. **No son objetivos de servicio.** Lo que la PoC mostró es
que un proceso sirve ~6,5 req/s de este mix y satura con 1-2 VUs: p95 0,9 s
a 3 VUs, 3,6 s a 10, 7-17 s a 20, 11,1 s en la rampa a 50, siempre sin errores.
Es el hallazgo DEF-15 ([DEFECTOS.md](DEFECTOS.md)); cuando se cachee la ventana
activa por ciclo, los umbrales bajan y la herramienta mide la ganancia con el
mismo script.
