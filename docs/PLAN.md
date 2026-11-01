# Plan de implementación

Objetivo: entregar proyecto ejecutable sin datos inventados y con límites medidos.
1. Dominio/API: pruebas de desconocidos, clasificación, filtros, deduplicación, historial y autenticación; implementar persistencia y endpoints.
2. Extracción: pruebas con fixtures claramente sintéticos de HTML, robots y URLs; implementar conectores y worker. Intentar ejecución contra fuentes reales y guardar informe.
3. Android: Compose, Room, Retrofit, DataStore, favoritos e historial personal, filtros, ajustes y notificación local; compilar si hay SDK y acceso a dependencias.
4. Entrega: instalación Windows y Docker, migración, manual, matriz de aceptación, pruebas y archivo ZIP.

Revisión: HTTP 200 nunca significa disponibilidad; cambios conservan favoritos; null no es envío gratis; robots/error no borran catálogo; destinos desconocidos no pasan filtro confirmado.

## Continuación: nube sin PC (2026-11-01)

El usuario confirma disponer de cuenta GitHub. Preparar ejecución periódica en GitHub Actions y catálogo estático en GitHub Pages. Mantener compatibilidad de la APK v0.1 con `/v1/offers` y `/v1/runs` como archivos JSON sin extensión, una sola página de hasta 10.000 ofertas. Probar esa compatibilidad HTTP localmente; la publicación en Pages requiere validación posterior. Conservar estado de ofertas/intervalos en JSON público sin secretos ni información del móvil. No activar fuentes nuevas ni declarar ingestión real mientras no funcione. No publicar hasta poder acceder a la cuenta; no asumir que confirmar cuenta equivale a una conexión verificada.
