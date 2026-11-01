# FreeFinder en GitHub: sin PC encendido

Este modo ejecuta trabajos finitos en GitHub Actions y publica un catálogo
estático en GitHub Pages. No necesita un servidor FastAPI siempre encendido,
un dominio propio ni una API de IA de pago. La APK v0.1 consulta las rutas
`/v1/offers` y `/v1/runs`; el exportador genera esos mismos archivos JSON sin
extensión. La compatibilidad HTTP local se prueba automáticamente; debe
comprobarse también contra la URL real de Pages antes de dar la instalación
por terminada.

## Estado de esta entrega

El código de nube está preparado y probado localmente. **Todavía no hay
repositorio creado, Pages publicado ni tarea activada en tu cuenta.** Tener
cuenta GitHub no implica que ChatGPT ya pueda acceder a ella. Instala y conecta
el complemento GitHub y continúa en este chat para completar la publicación.

La limitación de las fuentes sigue vigente: el alojamiento no produce ofertas
si no hay una fuente accesible y autorizada. No se incluyen ofertas de ejemplo.

## Qué será público

- Código de FreeFinder y configuración del trabajo.
- Ofertas observadas, URLs de evidencia, fechas y estados.
- Resultados de ejecuciones con errores reducidos a su categoría.

Las notas, favoritos, gastos anotados y fechas personales siguen en Room en
el teléfono. No se envían a GitHub. Nunca subas `.env`, `freefinder.db`, claves,
credenciales de marketplaces ni copias de datos privados.

## Preparación en la cuenta (una vez conectada)

1. Crear un repositorio público nuevo llamado `freefinder`, con estos archivos
   en su raíz (no dentro de una carpeta adicional llamada FreeFinder).
2. Revisar que no contiene archivos privados. El ZIP de entrega ya los excluye.
3. Settings → Pages → Build and deployment → Source → GitHub Actions.
4. Settings → Actions → General: permitir los workflows y las acciones
   oficiales de GitHub utilizadas. El trabajo pide permisos acotados para
   guardar el estado público y publicar Pages. No necesita un token personal.
5. Si hay reglas de rama o revisión del entorno github-pages, conservarlas y
   resolver su aprobación: no desactivarlas para forzar el despliegue.
6. Actions → FreeFinder cloud catalog → Run workflow en la rama predeterminada.
7. Abrir la URL devuelta por el despliegue. No se debe inventar una URL antes
   de que GitHub confirme el dominio/ruta efectivos.
8. Comprobar `/health`, `/v1/offers?limit=100&offset=0` y `/v1/runs` en esa URL.
   Deben responder HTTP 200 con JSON directo y sin redirección; la APK no sigue
   redirecciones por seguridad. Confirmar que `total` coincide con todos los
   elementos exportados. El catálogo puede estar vacío si falló la fuente.
9. En la APK → Ajustes → URL del backend: pegar la URL base de Pages, con la
   carpeta del repositorio y barra final. Guardar y sincronizar.

## Frecuencia real

El workflow está configurado cada seis horas, al minuto 17 UTC. El proveedor
puede retrasar o descartar ejecuciones; no es un servicio con horario exacto.
Cada fuente conserva además su intervalo mínimo (USGS: 24 h en la configuración
actual), de modo que una ejecución puede registrar que aún no toca revisar.
Las programaciones se ejecutan solo desde la rama predeterminada. GitHub puede
desactivar programaciones de repositorios públicos tras periodos de inactividad;
revisa el estado en Actions. Nada de esto está activado hasta publicar el repo.

La fecha de exportación de archivos no significa que una fuente se haya revisado
con éxito. El estado publica ambas fechas por separado. Un error mantiene las
observaciones previas y conserva su fecha de comprobación, sin inventar datos.

## Límites y mantenimiento

- GitHub Pages es estático: la búsqueda y los filtros se ejecutan en el móvil.
  No ejecuta FastAPI, PostgreSQL ni solicitudes de productos.
- El snapshot contiene hasta 10.000 ofertas en una única respuesta compatible
  con la APK. Si supera el límite se detiene la publicación; no se trunca.
- Se muestran 100 ejecuciones y se conservan además los últimos intentos de
  cada fuente para respetar sus intervalos, junto con 1.000 snapshots de cambios.
  La fecha de la última revisión satisfactoria se conserva por separado. El historial Git puede conservar versiones anteriores públicamente.
- Una ejecución tiene un máximo de 15 minutos; sin evasión de 403, captcha,
  robots o condiciones de uso.
- Actions y Pages tienen límites y políticas del proveedor. El diseño usa
  runners estándar y repositorio público; no configura recursos de pago ni
  permite prometer gratuidad o disponibilidad perpetuas.
- Desactivar el workflow detiene las búsquedas, pero Pages conserva el último
  catálogo publicado. La app muestra la última comprobación de cada oferta.

## Referencias oficiales

- https://docs.github.com/en/actions/concepts/billing-and-usage
- https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule

## Protección de publicación

El exportador acepta una lista explícita de campos de oferta/evidencia. Rechaza
URLs con credenciales, puertos no estándar o parámetros no aprobados para
publicación; un fallo conserva el catálogo público anterior. Los cambios de
repositorio ajenos al estado se integran con rebase y hasta tres intentos de
push; nunca se fuerza el historial ni se resuelven conflictos automáticamente.

Las pruebas Git/Bash del backend se omiten en Windows si faltan esas herramientas;
se ejecutan completas en el runner Linux de la nube.
