# FreeFinder · diseño de la primera versión

Decisión de implementación: Android nativo (Kotlin/Compose, minSdk 34), caché Room, preferencias DataStore, sincronización WorkManager. Backend FastAPI/SQLAlchemy compatible SQLite para instalación individual y PostgreSQL para despliegue. Worker separado, sin API de IA obligatoria. El catálogo empieza vacío: únicamente los conectores lo rellenan.

Flujo: fuente autorizada → robots y política de acceso → descubrimiento de enlaces → extracción conservadora → normalización URL → persistencia transaccional con evidencia y revisiones → API paginada → caché Android. Los marcadores privados permanecen en el teléfono y sobreviven a la sincronización.

Alternativas consideradas: búsquedas desde el teléfono (consume batería, no hace búsquedas cuando está apagado); servicios de búsqueda/IA comerciales (costes y dependencias). Se elige backend autoalojado, tal como pide la especificación. HTTPS obligatorio en release; HTTP de desarrollo solo para emulador/local.

Confianza: observar una campaña no verifica su solicitud. Por defecto pending; la extracción reconoce condiciones, exige revisión adicional antes de verified. Ningún campo territorial se deduce de un dominio .es. Desconocido = null/unknown, nunca cero. No se publican imágenes sin permiso. No se envían formularios.

Seguridad: fuentes administradas en archivo, lista cerrada de hosts, IP públicas y comprobación por cada redirección, sin endpoint de importación de URL, token para ejecutar tareas, límites de tamaño/tiempo, robots fail-closed, desactivación al faltar política de uso. Debe mantenerse restricción de salida de red en despliegues sensibles para mitigar DNS rebinding.

Alcance: conectores HTML de descubrimiento por enlaces para fuentes oficiales; soporte opcional de feed JSON autorizado. Los marketplaces con acceso restringido se documentan como no integrados, sin simular APIs. No se promete descubrir todo Internet. La frecuencia del worker es global y respeta el mínimo de cada fuente. IA, push remoto, verificación de carrito y descubrimiento abierto son ampliaciones.
