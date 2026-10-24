# QA y QC en OnTimeAI

QA (aseguramiento) trabaja sobre el **proceso** y previene; QC (control)
trabaja sobre el **producto** y detecta. Clasificación de lo que el proyecto
hace hoy, con la misma consigna que la clase del 14/09.

| Práctica del proyecto | QA o QC | Por qué |
|---|---|---|
| Plan de pruebas versionado con criterios de entrada y salida | QA | define cómo se trabaja antes de que exista el cambio |
| Un PR por cambio, con descripción del porqué, revisado | QA | estándar de proceso; la revisión en sí es QC del artefacto |
| Gate de complejidad con trinquete | QA | impone una regla al proceso; el run rojo puntual es QC |
| Cobertura mínima sobre código nuevo (80 %) | QA | regla de proceso: el código nace probado |
| Ejecutar la suite en cada push y PR | QC | detecta defectos en el artefacto concreto |
| Test de regresión por cada defecto corregido | QC (el test) y QA (la regla de que siempre exista) | el test verifica el producto; la obligación mejora el proceso |
| Smoke post-deploy | QC | verifica el despliegue concreto |
| Stress y soak con umbrales | QC | mide el producto bajo carga |
| Vigía con alertas Telegram | QC en producción | detecta fallas del producto en operación |
| Registro de defectos con pasos, esperado y obtenido | QC | documenta defectos hallados |
| Riesgos priorizados por probabilidad × impacto | QA | decide dónde probar más antes de probar |
| Matriz ISO 25010 y objetivos medibles | QA | fija qué significa calidad para este sistema |
| Plan de contingencia y simulacro mensual | QA | prepara el proceso para la falla |
| Documentar cada decisión técnica en `docs/` del repo | QA | reduce el riesgo de que un cambio futuro repita el error |
| Auditoría del Backend del 2026-08-09 | QA | revisión del proceso y la arquitectura, no de un bug |
| Secretos exigidos sin valor por defecto (#22) | QA | cambia la regla; antes un deploy olvidadizo arrancaba igual |
| Verificación de que el job arranca sólo con `requirements-job.txt` | QC | prueba el artefacto (la imagen) |

## Independencia

El autor del cambio escribe los tests unitarios; otra persona del grupo revisa
el PR y confirma que el criterio de salida se cumple. En la defensa, la nota
individual depende de poder explicar cualquier parte, así que la revisión
cruzada también sirve para repartir el conocimiento.

## Lo que falta de QA

Auditoría periódica del proceso (¿se siguen los criterios de salida?): se
propone una revisión mensual del registro de defectos y de `mediciones/`.
