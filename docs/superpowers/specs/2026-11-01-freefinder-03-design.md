# FreeFinder 0.3 — diseño y cobertura

Objetivo autorizado: mejorar la estética y el icono, mostrar más productos reales y aclarar qué plataformas están disponibles. La especificación original ya define tarjetas visuales, Material 3, fotos grandes, categorías con iconos, navegación inferior, idiomas y modo oscuro. El usuario pide continuar sin una ronda adicional de decisiones.

Decisión de implementación: mantener Kotlin/Compose y el backend existente; paleta bosque/menta, icono vectorial adaptable de regalo con lupa, catálogo en cuadrícula adaptable (una columna con fuente grande), tarjetas compactas, fotos sin recortar, estados comprensibles y ficha completa. Se descarta una portada web o imágenes de maqueta porque no mejorarían la APK real. Se conserva la información desconocida de envío y la clasificación conservadora.

Fuentes: apartado independiente con plataformas solicitadas y estados claros: automatizada, acceso externo o invitación/permisos pendientes. Un directorio de plataformas no se contará como productos. La investigación de nuevas campañas debe revisar condiciones, robots y permisos, sin eludir bloqueos ni copiar imágenes sin licencia. No se promete cubrir todo Internet.

Entrega: APK 0.3, código en GitHub, backend probado y publicación en Pages. La clave de firma de 0.2 no está disponible: no se desinstala ni se sobrescribe la app instalada. La nueva app se instala junto a ella para conservar los datos originales. La distribución estable con actualizaciones requiere una clave persistente protegida; documentar limitación.

Plan: implementar diseño e iconos; integrar cobertura de fuentes; integrar solo nuevos conectores que superen revisión; probar backend/JVM/lint/compilación; comprobar catálogo y descarga públicos. No declarar una integración operativa a partir de una página genérica o un simple enlace activo.

## Revisión independiente
Se corrigieron: licencia de imagen enlazable y acceso a créditos desde cada tarjeta; una sola columna con fontScale>1.2; estado territorial visible junto al coste; tratamiento explícito de ambos destinos y recogida; estado de conector desactivado sin etiqueta sin traducir.
