# Estado y criterios de aceptación

**Versión técnica inicial. No es todavía el servicio completo listo para uso real.** Las pruebas con fixtures no sustituyen una ingestión real o una prueba en teléfono.

| Criterio | Estado |
|---|---|
| Instalar/abrir Android | Código implementado; resultado de compilación en VALIDACION.md. Sin prueba en OnePlus físico. |
| Productos de al menos una fuente real | **No conseguido en este entorno.** No se ha importado catálogo real. |
| Fotos/enlaces auténticos | Modelo y apertura implementados; fotos desactivadas sin permiso. Falta prueba con producto real en app. |
| Filtro por categoría | Implementado Android/API; pruebas de lógica. |
| Filtro ES/AD | Implementado. Desconocidos no pasan el filtro confirmado; no hay envíos reales confirmados. |
| Gratis/reembolso/sorteo/préstamo | Tipos separados, filtros y clasificación heurística conservadora. |
| Transporte conocido | Modelo y presentación; sin cálculo de carrito/código postal. |
| Información no verificada | Estados, evidencias y desconocidos implementados. HTTP 200 nunca eleva a verified. |
| Favoritos | Room implementado; falta prueba instrumentada. |
| Actualizar sin reinstalar | Sync paginada/transaccional; falta validación con ingestión real. |
| Historial actualización | API probado, pantalla implementada. |
| Notificación de prueba | Canal, permiso y botón implementados; pendiente teléfono. |
| Abrir página original | Intent HTTPS implementado; pendiente teléfono. |

## Alcance por fase

1. Android: navegación, tarjetas, categorías, filtros principales, tema, idiomas, caché, favoritos, solicitado/recibido, notas y ajustes. No están todas las secciones editoriales del inicio ni filtros avanzados.
2. Backend: API, SQLite/PostgreSQL, migración, worker, historial y sync. PostgreSQL/Docker entregados sin prueba de contenedores.
3. Fuentes: adaptador USGS y HTML por enlaces; fuentes restringidas desactivadas. Falta una fuente accesible/autorizada demostrada. No hay productos manuales ni ficticios.
4. Verificación: fecha, URL, hash, modalidades y desconocidos. Faltan extracción completa de condiciones, fechas, territorios, impuestos y carrito/solicitud.
5. Automatización: intervalos, bloqueo, registro, WorkManager y novedades por IDs. Faltan ranking de fuentes, descubrimiento de dominios, caducidad/reaparición, push y riesgo avanzado.
6. QA: pruebas backend, migración SQLite, revisión independiente y compilación Android según VALIDACION.md. Faltan pruebas instrumentadas, rendimiento y OnePlus real.

## Decisiones relevantes

- Se prioriza catálogo vacío sobre ofertas fabricadas o copiadas contra condiciones de la fuente.
- Backend sin publicar; no continuará buscando al cerrar el entorno.
- Sin IA obligatoria, n8n o API de pago.
- Sin cobertura universal de marketplaces ni detección completa de fraude.
- Desaparecidos conservados en historial/caché y separados del catálogo activo.
- APK debug, si se incluye: para pruebas, sin firma de producción.
