# FreeFinder — Android + backend · 0.4.0

Versión de prueba Android 14+ con diseño neutro (blanco/negro/gris). La vista inicial busca productos completos con precio anunciado cero y sin compra adicional conocida; separa muestras, sorteos, reembolsos y préstamos. Se han añadido lectores reales de Bemz, Kvik, un feed público de anuncios y productos completos a cero de MGL. **No están conectados todos los marketplaces**. El catálogo de MGL es material de divulgación religiosa: no sustituye una integración general de electrónica o ropa. No se han realizado pedidos ni se garantiza el envío a ES/AD.

## Uso con el PC apagado

El catálogo está publicado en [GitHub Pages](https://victorvnn.github.io/freefinder/) y se revisa mediante GitHub Actions cada seis horas, respetando los intervalos de cada fuente. Pages sirve una instantánea JSON, no un servidor de búsqueda en tiempo real. Las ejecuciones programadas pueden retrasarse.

[Descargar APK 0.4.0](https://victorvnn.github.io/freefinder/downloads/freefinder-0.4.0.apk). Se instala como **FreeFinder 0.4** junto a las aplicaciones anteriores. No es necesario desinstalarla: sus favoritos y notas permanecen allí, sin transferencia automática. La URL pública viene preconfigurada; pulsa Sincronizar catálogo. En Ajustes, guarda las preferencias para programar las revisiones locales y configura el permiso de notificaciones si quieres avisos.

Se muestran las imágenes cuya licencia se ha revisado, con crédito y evidencia. Los campos de transporte y cargos desconocidos siguen vacíos, nunca se convierten en cero. Consulta [las mejoras y límites de esta versión](docs/MEJORA_02.md).

## Diseño y fuentes

Nuevo icono adaptable de regalo y lupa; paleta neutra blanca, negra y gris; catálogo con tarjetas en cuadrícula; una columna con texto grande; indicadores de carga y error de imagen; créditos y enlaces de licencia. La pestaña Fuentes reúne las plataformas del pliego y distingue los lectores automáticos habilitados de los accesos externos sin automatización. **Un enlace de plataforma no es una oferta ni una integración terminada.**

## Validación

Pruebas del backend, pruebas JVM de Android, lint y compilación del APK ejecutados en GitHub Actions. No se ha probado físicamente esta versión en el OnePlus Nord 4. Los documentos de validación de 0.1.0 son históricos; la ejecución actual se encuentra en la pestaña Actions.

## Contenido

- `android/`: proyecto Android Studio, Kotlin, Compose/Material 3, Room, DataStore, Retrofit y WorkManager. Android 14 o superior.
- `backend/`: FastAPI, persistencia SQLite/PostgreSQL, migración Alembic, worker independiente, extracción conservadora, historial de cambios y ejecuciones.
- `scripts/`: instalación y arranque para Windows.
- `docs/INSTALACION_WINDOWS.md`: empezar paso a paso.
- `docs/MANUAL_USO.md`: manual en castellano.
- `docs/ARQUITECTURA.md` y `docs/DESARROLLO.md`: ampliación, seguridad y contrato de conectores.
- `docs/FUENTES.md`: fuentes, restricciones y costes.
- `docs/ESTADO.md`: matriz honesta de implementación y aceptación.
- `docs/VALIDACION.md`: pruebas ejecutadas y límites de la validación.

## Inicio rápido del backend (Python 3.12+)

Desde `backend/`:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# Sustituir ADMIN_TOKEN por un valor aleatorio en .env.
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe run_api.py
```

En otra terminal, misma carpeta:

```powershell
.\.venv\Scripts\python.exe run_worker.py
```

Abrir http://127.0.0.1:8000/docs . No hay cuentas de usuario ni compras automatizadas. Nunca introducir contraseñas de marketplaces.

El token de administrador solo se usa para el endpoint de ejecución. No se guarda en Android. La sincronización del móvil descarga los datos que ya tiene el servidor; no lanza una búsqueda en Internet.

## Costes

Código sin anuncios ni API de IA obligatoria. Un ordenador propio encendido requiere electricidad e Internet. Un alojamiento externo, dominio, backups o APIs comerciales pueden costar dinero. No se incluye un servidor gratuito permanente ni una promesa de servicio activo.
