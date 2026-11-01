# FreeFinder 0.2: catálogo visual y cobertura transparente

Mantener el backend publicado y datos personales locales. Añadir crédito/licencia de imagen por oferta y carga visual con imagen ampliable. Mejorar inicio con recuentos, estado de sincronización, filtros de marca/plataforma/estado y filtros vacíos claros. Configurar por defecto la URL ya publicada y traducir los errores de configuración. Añadir directorio separado de plataformas/programas con estado automático/manual/restringido: nunca confundir una página genérica con un producto.

Ampliar descubrimiento por fuentes públicas permitidas, con presupuesto, robots y evidencias. Conectores adicionales no se consideran operativos hasta una ejecución real. Publicar APK 0.2 mediante compilación CI y descarga HTTPS; verificar tests y compilación antes de entregarla. No prometer cobertura de todo Internet ni fotos con derechos desconocidos.

## Estado de la cobertura
No se busca «todo Internet». Hay dos adaptadores automáticos: USGS (cuatro páginas educativas de descubrimiento) y Agrisera (colección de pósteres impresos). Las búsquedas están limitadas por robots, permisos y presupuesto de peticiones. Amazon, Temu, SHEIN y las restantes plataformas del pliego no tienen conectores operativos en esta versión. Añadir un nombre a un directorio no equivale a integrar una fuente.

Agrisera: la página ofrece copias impresas sin coste del producto mediante suscripción al boletín. Cada PDF sirve para identificar un póster real y la URL de solicitud abre las instrucciones del editor. No se ha solicitado ningún ejemplar. Transporte, residencia, stock individual y posibles cargos permanecen desconocidos. Las imágenes no se reproducen porque su permiso educativo no cubre claramente un catálogo general.

USGS: dos referencias de imágenes revisadas y enlazadas a sus publicaciones originales, con créditos y fuente de derechos. Esta lista solo configura imágenes: no introduce ofertas manuales ni sustituye la comprobación automática del producto. Otros productos sin permiso revisado siguen sin imagen.

## Android 0.2.0
Añade cabecera con número de oportunidades, filtros de marca/plataforma/estado combinables, inclusión explícita de destinos desconocidos, botón para quitar filtros, mensaje para búsquedas sin coincidencias, imágenes grandes con créditos y URL pública preconfigurada. Los datos personales permanecen en Room.

Compilación en GitHub Actions con Java 17 y Gradle 8.9; ejecuta pruebas JVM, lint y assembleDebug. APK descargable desde Pages después de una compilación correcta. La clave de desarrollo original no está disponible: se usa un identificador distinto org.freefinder.preview, visible como FreeFinder 0.2. Se instala junto a la original, que conserva sus datos. Los favoritos no se transfieren automáticamente. El APK publicado de esta versión se conserva sin sobrescribir su firma en siguientes ejecuciones. No se publica ninguna clave privada en el repositorio. Antes de distribución estable se debe configurar una clave de publicación persistente como secreto protegido.

Las ejecuciones programadas conservan el APK publicado en Pages. El catálogo sigue actualizándose con el PC apagado. GitHub Actions puede retrasar ejecuciones y sus políticas/cuotas pueden cambiar; no se promete disponibilidad continua de un servidor ni búsquedas instantáneas.
