# Validación ejecutada · 1 de noviembre de 2026

## Backend

- `python -m pytest -q`: **19 pruebas superadas**. Incluyen clasificación, precio de producto frente a envío gratis, reembolso sin inventar precio inicial, desconocidos, filtros combinados, duplicados, snapshots, autenticación, validación de consulta, bloqueo de URLs, descubrimiento de enlaces, redirecciones bajo robots y registro de fallo de inicialización del cliente.
- API arrancada con Uvicorn y comprobada mediante HTTP real en localhost: `/health` y `/v1/offers` correctos. Catálogo vacío, sin fixtures cargados. Ver `api-smoke-test.json`.
- Alembic ejecutado contra una base SQLite nueva: migración `0001 (head)` correcta.
- `python -m compileall -q app`: correcto.
- Una advertencia de compatibilidad futura en el cliente de pruebas de Starlette/httpx; no fue un fallo de las pruebas.

## Android

La versión final se compila con Gradle 8.9, JDK 17 y Android SDK 35. El resultado exacto, tests y lint se recoge en `android-validation.txt`, generado a partir de la compilación final. Se entrega APK debug firmada para pruebas, no una publicación de producción.

Los tests JVM cubren filtro de desconocidos, exclusión de compra, conservación explícita, categoría/modalidad y ambos destinos con límite de portes. No son pruebas instrumentadas de UI, Room, notificaciones o hardware.

## Fuentes externas

**No se ha demostrado una ingestión real completa.** El worker seguro encontró una limitación de resolución DNS. En comprobaciones HTTP de diagnóstico, robots de USGS fue accesible pero su catálogo devolvió HTTP 403. No se ha omitido la defensa de IP pública ni se han usado técnicas para evadir el bloqueo. No se han introducido registros manuales para sustituir la ingestión.

Fellowes y Danone permanecen desactivadas por restricciones de uso. Las campañas localizadas durante investigación web no equivalen a ofertas obtenidas por el backend ni solicitudes verificadas.

## No validado

- Instalación, apertura y uso en OnePlus Nord 4 físico o emulador Android.
- Entrega real de la notificación de prueba en un dispositivo.
- Sincronización contra un backend con catálogo externo real, fotografías autorizadas y costes territoriales.
- Solicitud, stock, carrito, envío/residencia España o Andorra.
- PostgreSQL, Docker y despliegue HTTPS de producción.
- Rendimiento, accesibilidad y consumo en uso prolongado.

Por tanto, **no se considera cumplida la aceptación completa del proyecto**. Es una base técnica compilable para continuar, con los bloqueos y pendientes explícitos.

## Advertencia de compilación

Room usa kapt; lint recomienda migrar a KSP para mejorar tiempos de compilación. No se considera un error funcional. La compilación incremental encontró un conflicto de archivos DEX tras cambios de recursos: se repite la validación con `clean` para comprobar el paquete final desde cero.

## Continuación nube sin PC

Se añadió exportación de catálogo estático compatible con las rutas de la APK v0.1, restauración de metadatos públicos, conservación de intervalos por fuente y workflow GitHub Actions/Pages. El backend pasa ahora 29 pruebas, incluyendo HTTP real contra archivos sin extensión, retención, rechazo de URLs con secretos y un conflicto Git real simulado localmente entre dos clones. Android no se ha modificado y no se ha recompilado en esta continuación. Falta publicar en GitHub, validar las rutas reales de Pages y conseguir ingestión operativa.
