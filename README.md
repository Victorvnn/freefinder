# FreeFinder — Android + backend · 0.1.0

Primera versión técnica. **No es todavía el servicio completo solicitado y no cumple la aceptación de catálogo real operativo.** No incluye productos inventados ni una base de datos precargada. El catálogo puede permanecer vacío: hay que ejecutar el backend y disponer de una fuente accesible y autorizada.

## Uso sin PC encendido

Se ha añadido `.github/workflows/freefinder-cloud.yml` para ejecutar búsquedas en GitHub Actions y exportar un catálogo estático compatible con la APK v0.1 en GitHub Pages. La configuración y la conexión de la cuenta están pendientes. Empieza por `docs/NUBE_GITHUB.md`. La ingestión real sigue sin demostrarse; el alojamiento no sustituye esa validación.

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
