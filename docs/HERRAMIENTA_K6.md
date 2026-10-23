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

(Se completa con la tabla del PR `feat/stress-k6`: VUs, iteraciones, RPS,
p50/p95/p99, tasa de error y resultado de umbrales por escenario, local y en CI.)
