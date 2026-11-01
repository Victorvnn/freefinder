# FreeFinder 0.3.1 — validación real

- Backend: 40 pruebas correctas.
- Android: testDebugUnitTest, lintDebug y assembleDebug correctos.
- Emulador Android API 35 (Pixel 6): instalación correcta, lanzamiento de la actividad, primera sincronización real de 11 ofertas, capturas de modo claro, oscuro y escala de fuente 1.3; no se detectó FATAL EXCEPTION en AndroidRuntime.
- Revisión visual de capturas reales: cuadrícula de dos columnas; una columna con letra grande; imágenes auténticas; estados territoriales desconocidos visibles; nuevo icono. Se ajustó el contraste de las barras del sistema y se volvió a compilar y ejecutar la prueba.
- Una primera espera automatizada no detectó la pantalla a tiempo; se añadieron registros y capturas de diagnóstico. Las ejecuciones posteriores pasaron. No se atribuye el fallo inicial a una causa de la app no demostrada.
- Directorio: 29 entradas, 2 automáticas. Los 24 nombres del pliego están separados de los productos. No se ha añadido un conector no autorizado.
- Catálogo público: 11 ofertas reales, 10 imágenes con referencias de derechos, envío ES/AD desconocido conservado como tal.
- APK público: https://victorvnn.github.io/freefinder/downloads/freefinder-0.3.1.apk
- Ejecución final: https://github.com/Victorvnn/freefinder/actions/runs/41354950844

No se ha probado físicamente 0.3.1 en el OnePlus Nord 4. La apertura y sincronización de 0.2 sí fueron confirmadas por el usuario. El APK se firma con clave de desarrollo; al no disponer de la clave anterior se instala como aplicación separada FreeFinder 0.3 (org.freefinder.design), sin borrar 0.2 ni transferir automáticamente sus datos. Para distribución estable y actualizaciones se necesita configurar una clave persistente protegida.
