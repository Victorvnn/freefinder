# Documentación técnica

## Mapa del código

| Archivo/carpeta | Responsabilidad |
|---|---|
| `backend/app/domain.py` | Clasificación, normalización, extracción conservadora, totales con desconocidos |
| `backend/app/db.py` | Ofertas JSON extensibles, snapshots y ejecuciones; upsert por URL canónica |
| `backend/app/main.py` | API de lectura, filtros paginados, detalles, historial y ejecución protegida |
| `backend/app/worker.py` | Planificación, límites de fuente, bloqueo de proceso compartido, errores |
| `backend/app/connectors/safe_http.py` | HTTPS, hosts permitidos, resolución pública, robots y redirecciones |
| `backend/app/connectors/html.py` | Descubrimiento limitado por enlaces y extracción HTML |
| `backend/app/connectors/usgs.py` | Publicaciones físicas en papel, precio exacto cero y cargo de gestión |
| `backend/alembic/` | Migración inicial compatible SQLite/PostgreSQL |
| `android/.../Models.kt` | Modelo de intercambio y filtros locales |
| `android/.../Storage.kt` | Room y preferencias DataStore |
| `android/.../Repository.kt` | Retrofit, paginación, caché transaccional y archivo local |
| `android/.../CatalogViewModel.kt` | Estados y operaciones de UI |
| `android/.../MainActivity.kt` | Pantallas Compose |
| `android/.../Notifications.kt` | WorkManager y notificaciones locales |
| `android/.../Strings.kt` | Tabla de traducciones de interfaz ES/CAT/EN |

## API

OpenAPI interactivo en `/docs`, JSON en `/openapi.json`; copia de referencia en `docs/openapi.json`.

- `GET /health`: proceso disponible, sin afirmar búsqueda en directo.
- `GET /v1/offers`: texto, categoría, plataforma, marca, tipo, país, estado, máximo transporte, mínimo valor, conservación, orden y paginación. Límite 100 por página.
- `GET /v1/offers/{id}` y `/history`: ficha y hasta 100 versiones.
- `GET /v1/runs`: hasta 100 intentos de búsqueda.
- `GET /v1/sources`: fuentes registradas y sus limitaciones.
- `POST /v1/refresh`: requiere `Authorization: Bearer ADMIN_TOKEN`; no elude mínimos por fuente. La app no usa este endpoint.

El límite básico es de 120 peticiones por minuto e IP y proceso. En producción deben añadirse límites en el proxy y políticas de acceso al backend. No sirve como limitador global distribuido.

## Datos y evidencias

`offers.payload` conserva todos los hechos del modelo de intercambio como JSON. `null` es desconocido; cero solo se almacena cuando hay una observación explícita. Estados de envío: `confirmed`, `unavailable`, `unknown`. Los campos de coste y cargos existen por destino.

`evidence` contiene campo, URL, hora, método, hash de la respuesta y nota del alcance comprobado. No se almacena HTML completo de terceros. Un hash documenta la observación, pero **no permite reconstruirla ni demuestra por sí solo la veracidad del contenido**. Para auditorías fuertes se requiere una política de preservación de evidencias autorizada.

`revisions` conserva snapshots cuando cambian los hechos, excluyendo simples cambios de hora de comprobación. `runs` conserva intentos incluso fallidos. Falta una política de retención y compactación para despliegues prolongados.

La confianza actual es una constante conservadora por extractor, no un porcentaje estadístico de fiabilidad. La UI la denomina confianza de extracción. Nunca se transforma automáticamente una observación HTML en una solicitud verificada.

## Añadir una fuente

1. Comprueba API/feed oficial, condiciones de acceso, reutilización y permisos de imagen. Conserva la referencia y fecha; no trates robots como licencia.
2. Añade un adaptador en `app/connectors/` que reciba `source` y `SafeHTTP` y exponga `collect() -> list[dict]`.
3. Regístralo explícitamente en el worker. Los módulos no se cargan desde nombres suministrados por la red.
4. Añade la entrada a `sources.json`: ID, nombre, adaptador, hosts exactos, URL de arranque, mínimo de horas, URL de política y fecha de revisión. Activa únicamente una fuente cuyo uso haya quedado resuelto.
5. Extrae cada campo con evidencias propias. No derives países desde el dominio o una lista de países de un mapa. No derives precio de producto desde transporte gratis.
6. Para fotos, incorpora solo URLs y créditos cubiertos por permiso de uso; deja `image_url=null` mientras no exista.
7. Añade fixtures sintéticos bajo tests y una prueba de ingestión real sin autenticaciones o formularios. Guarda por separado el resultado real y la fecha.
8. Si hay 403/429, captcha o prohibición, detén la ejecución. No añadas técnicas de evasión.

El adaptador HTML general es intencionadamente conservador y no demuestra que cualquier sitio compatible se pueda integrar legalmente.

## Desarrollo y pruebas

```powershell
# backend, venv instalada
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m alembic upgrade head
# android
.\gradlew.bat testDebugUnitTest assembleDebug
```

Las pruebas automatizadas usan dominios y textos sintéticos claramente marcados. No validan condiciones comerciales de una web real. Los tests de redirecciones emplean transporte HTTP en memoria; las pruebas de dominio y API ejecutan lógica y persistencia reales.

## Despliegue

Para uso personal local se usa SQLite. Para varios procesos, PostgreSQL y un único worker. El bloqueo de archivo funciona en el despliegue Compose de un solo host con volumen compartido; no proporciona coordinación entre servidores diferentes. No escalar workers a varias máquinas sin sustituirlo por bloqueo/cola distribuida.

HTTPS debe terminar en un proxy administrado (por ejemplo Caddy/NGINX) antes de exponer la API. No se incluye dominio ni certificado de producción. El servidor de desarrollo escucha solo en localhost.

La defensa SSRF incluye hosts cerrados, IP públicas y validación en cada salto. Queda riesgo de DNS rebinding entre validación y conexión/proxy. Un despliegue sensible debe restringir salida hacia rangos privados en la red, además de estas comprobaciones. El runtime de esta entrega restringe DNS directo: el recolector falla cerrado en lugar de omitir la validación.

## Próximas ampliaciones necesarias

- Una fuente real accesible y autorizada con ingestión completa demostrada.
- Contrato tipado y validado para adaptadores; índices SQL y filtros en DB para grandes catálogos (ahora filtra en memoria).
- Extracción por campo de condiciones, fechas, portes territoriales y disponibilidad; revalidación de ofertas existentes, además del descubrimiento.
- Reglas de riesgo explicables y revisión humana de descartes. Ahora solo se muestran advertencias aportadas por el adaptador.
- Expiración/reaparición, recordatorios, bandeja de eventos y push opcional.
- Filtros de UI de marca, plataforma, fechas y estados; ahora backend tiene parte de ellos pero la app no los presenta todos.
- Pantalla de versiones y registro de fuentes en Android.
- Pruebas instrumentadas, accesibilidad, rendimiento y validación OnePlus real.
- Firma de distribución, migraciones Android futuras, exportación privada de notas y preferencias.

No están integrados n8n ni IA: no aportan una ventaja necesaria a esta primera versión y aumentarían las dependencias.
