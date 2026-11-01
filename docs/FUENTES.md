# Fuentes y límites técnicos

Revisión: 1 de noviembre de 2026. El catálogo no incorpora productos manuales. Una URL de arranque es un punto de descubrimiento, no un producto preintroducido.

| Fuente | Código | Activación | Resultado y limitación |
|---|---|---|---|
| USGS Store | Adaptador de catálogo físico y precio cero | Configurado para intentar revisión cada 24 h | No se ha conseguido una ingestión real completa: DNS restringido en ejecución segura y HTTP 403 en la página de catálogo durante el diagnóstico. No se evaden bloqueos. |
| Fellowes | Adaptador HTML general por enlaces | Desactivado | Condiciones restrictivas sobre redistribución, archivo y enlaces. No hay autorización obtenida. |
| Danone | Adaptador HTML general por enlaces | Desactivado | Condiciones restrictivas sobre extracción y reutilización. No hay autorización obtenida. |
| Otros marketplaces/programas de pruebas de la especificación | No implementados | No activos | No se han obtenido contratos, acceso autorizado a sus APIs ni permiso para extracción. |

## Referencias oficiales revisadas

- USGS catálogo: https://store.usgs.gov/educational-products
- USGS robots: https://store.usgs.gov/robots.txt
- USGS copyright: https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits
- Fellowes condiciones: https://www.fellowes.com/es/es/misc/pg/terms-of-use
- Danone condiciones: https://www.danone.es/aviso-legal/
- Android Compose: https://developer.android.com/develop/ui/compose/bom
- FastAPI despliegue: https://fastapi.tiangolo.com/deployment/docker/

Para USGS se limita la extracción a metadatos factuales de publicaciones gubernamentales; no se reutilizan imágenes ni logotipos. **Esto no equivale a un acuerdo de integración.** La política y la accesibilidad deberán reconfirmarse antes de un servicio público. El adaptador no permite descargar contenido si la comprobación de robots o IP falla. Se puede desactivar en `backend/sources.json`.

La búsqueda web de desarrollo encontró páginas de productos de papel a precio cero en USGS con un cargo de gestión publicado. Esas observaciones no se han importado como registros manuales para fingir una ingestión. No se confirma envío a España ni Andorra.

## Política del recolector

- Solo HTTPS y hosts administrados, sin credenciales en URLs.
- Comprobación de IP pública y robots en cada destino de redirección.
- Sin acceso al carrito, búsqueda prohibida por robots, registro, login o formularios.
- Pausa mínima 3 segundos; máximo 20 páginas por pasada del adaptador USGS.
- Timeout de 20 segundos y respuesta de hasta 2 MB.
- Un fallo se registra; nunca produce ofertas de sustitución.
- Los reintentos ocurren en la siguiente ventana permitida; no hay bucles sobre un 403.
- El intervalo por fuente puede ser superior a la preferencia global.

No se ha implementado un servicio que descubra dominios nuevos por toda Internet. Ampliar requiere revisar permisos y añadir una fuente/conector. Una API de búsqueda externa podría ayudar pero sus cuotas y costes deben evaluarse por separado.

## Costes previsibles

| Elemento | Situación |
|---|---|
| App y backend | Sin anuncios, suscripción o API comercial obligatoria |
| PC propio | Electricidad, conexión y mantenimiento; debe estar encendido |
| Servidor externo | Coste según proveedor y recursos; ningún plan gratuito garantizado |
| HTTPS | Puede usar certificados gratuitos; requiere configuración y, habitualmente, dominio o acceso apropiado |
| PostgreSQL/SQLite | Software gratuito; almacenamiento y backups consumen recursos |
| APIs de búsqueda o IA | Opcionales; pueden cobrar por uso, actualmente no integradas |
| Distribución en Play Store | No incluida; consultar condiciones y coste del programa antes de publicar |
| Solicitudes de productos | Transporte, gestión, impuestos o adelantos dependen de cada promoción; nunca se pagan automáticamente |
