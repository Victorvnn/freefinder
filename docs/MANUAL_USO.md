# FreeFinder · Manual de uso

## Qué hace esta versión

FreeFinder consulta un catálogo mantenido por tu backend. Puede mostrarlo sin conexión después de sincronizar. No tiene anuncios, pagos integrados ni rastreo comercial. No busca continuamente desde el teléfono.

**No hay un catálogo precargado.** La integración real debe conseguir acceder legal y técnicamente a una fuente antes de que aparezcan productos. Los datos sintéticos de las pruebas no se cargan en la aplicación.

## Explorar

- Escribe texto para buscar por nombre, marca o plataforma.
- Pulsa una categoría.
- Selecciona ES, AD, ambos o recogida. Los filtros ES/AD muestran únicamente territorios confirmados. Un país desconocido no pasa el filtro.
- Abre Filtros para elegir modalidad, orden, máximo de portes y conservación confirmada.
- «Máximo de portes» compara importes de la moneda original. No convierte divisas; evita comparar costes de distintas monedas como si fueran equivalentes.
- Pulsa actualizar para descargar el catálogo del servidor. Eso no obliga a las fuentes a actualizarse en ese instante.

## Comprender una oferta

Una oferta `Pendiente de verificar` solo contiene observaciones automatizadas. No garantiza unidades, aceptación de la solicitud o entrega. Las campañas de selección, reembolso, sorteo y préstamo tienen modalidades separadas.

`0.00` es distinto de `—`. El guion significa desconocido. Si no se conocen portes aparece «Pendiente de comprobar en el carrito». El total solo se calcula cuando se conocen precio, transporte y cargos adicionales para ese destino.

Las cantidades se muestran con su moneda de origen. Un reembolso no equivale a no adelantar dinero. Un préstamo debe devolverse. La ausencia de indicaciones de fraude no significa que una tienda sea segura.

No se muestran imágenes si no hay un permiso de uso comprobado. En ese caso se utiliza un icono. No se sustituyen fotografías por imágenes inventadas.

## Solicitar un producto

Pulsa «Ver oferta original». FreeFinder abre el navegador; revisa allí condiciones, residencia, costes y disponibilidad. La aplicación no rellena formularios, crea cuentas ni compra en tu nombre. Tener una dirección española no acredita residencia española.

## Favoritos y seguimiento

El corazón guarda un favorito únicamente en el teléfono. En la ficha puedes marcar solicitado/recibido, añadir fecha, gastos pagados con moneda y notas. Los gastos son anotaciones personales; no se suman automáticamente entre divisas.

Si una oferta desaparece del catálogo tras una sincronización completa, se conserva para historial como «Solo en caché». No aparece como oportunidad activa. Los favoritos y notas permanecen.

## Historial

Muestra intentos descargados del backend, con hora, fuente, resultado y error. Distingue una sincronización del móvil de una búsqueda ejecutada por el servidor. La API también ofrece versiones de cada oferta en `/v1/offers/{id}/history`; la pantalla de la aplicación todavía no ofrece la comparación de versiones.

## Ajustes y avisos

- Idioma: castellano, catalán o inglés. Los textos recibidos del backend pueden conservar su idioma original.
- Tema: sistema, claro u oscuro.
- Frecuencia del móvil: manual, 1, 3, 6, 12 o 24 horas. Android decide el momento efectivo; no es un temporizador exacto.
- Avisos: una categoría opcional y un destino confirmado opcional.
- Silencio: 22:00–08:00 según hora local del teléfono. Los avisos silenciados no se acumulan para la mañana.
- El aviso de prueba permite comprobar el permiso de Android sin inventar una oferta.
- El código postal es solo una preferencia local en esta versión; no calcula portes.

La primera sincronización manual no envía un aviso masivo. Los avisos de novedades los genera el worker local al detectar IDs nuevos. Aún no hay avisos de caducidad, reaparición o push remoto.

## Privacidad

No se almacenan credenciales de marketplaces ni dirección completa. Favoritos, notas y preferencias están en el almacenamiento privado de Android. Desinstalar o borrar los datos de la app elimina esos datos; no hay copia de seguridad remota ni sincronización de notas entre dispositivos.
