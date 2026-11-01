# Revisión independiente de la primera versión

Se solicitó una revisión estática independiente del código y de la arquitectura. Se señalaron cuatro problemas importantes:

1. Arranque simultáneo del worker y migración: se añadió healthcheck del API y dependencia de estado sano.
2. Máximo de envío con ambos destinos: Android ahora exige que los dos importes sean conocidos y estén bajo el límite.
3. Ofertas desaparecidas: una sincronización completa las marca como solo caché, las oculta del catálogo activo y las conserva para historial. Una sincronización fallida no las archiva.
4. «Envío gratis» interpretado como producto cero: se exige una afirmación explícita del producto/muestra gratuito; reembolso no inventa precio inicial cero. Se añadieron regresiones, vistas fallar antes de corregir el extractor.

La revisión no valida ingestión real, condiciones comerciales, comportamiento de teléfono ni todos los criterios del producto. Las carencias conocidas siguen en ESTADO.md.

## Revisión independiente del modo nube

Se corrigieron pérdida de fechas satisfactorias tras retención, pérdida del intervalo de una fuente lenta al acumular intentos de otras fuentes, exportación excesiva de campos y URLs sensibles, y fallo de push ante cambios concurrentes del repositorio. Las regresiones se observaron fallar antes de corregirlas y la suite final quedó verde. Sigue pendiente comprobar GitHub Pages real.
