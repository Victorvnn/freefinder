# Instalación paso a paso en Windows

## 1. Preparar el equipo

1. Descomprime el ZIP en `C:\FreeFinder`. Evita trabajar dentro del ZIP.
2. Instala Python 3.12 o superior, con Python Launcher (`py`).
3. Instala Android Studio y deja que descargue Android SDK Platform 35 y Build Tools. Usa JDK 17 para este proyecto. La descarga inicial de herramientas y dependencias necesita Internet y espacio libre.
4. No hace falta registrar cuentas en marketplaces, contratar IA ni pagar una API.

## 2. Instalar el servidor local

Abre PowerShell en `C:\FreeFinder` y ejecuta:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-backend.ps1
```

El permiso se aplica solo a ese proceso, sin cambiar permanentemente la política del equipo. El script genera un token aleatorio si aún no hay `.env`. No reemplaza un `.env` existente.

En una primera ventana:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-api.ps1
```

En otra ventana:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-worker.ps1
```

Visita http://127.0.0.1:8000/health y http://127.0.0.1:8000/docs . Las ventanas deben permanecer abiertas. Si cierras el PC, el backend y sus revisiones se detienen.

Consulta http://127.0.0.1:8000/v1/runs : una ejecución `error` o un catálogo vacío no significa que haya ofertas disponibles. El primer intento puede fallar por restricciones de la fuente o red. No cambies de identidad ni intentes saltarte un bloqueo.

## 3. Instalar la APK de pruebas

Si descargas `FreeFinder-0.1.0-debug.apk`, ábrela en el teléfono y autoriza la instalación desde esa aplicación de archivos cuando Android lo solicite. Esta APK necesita el backend configurado; no lleva productos incluidos. Es una compilación debug para pruebas, no una app publicada en Play Store.

## 4. Abrir el proyecto Android

1. Android Studio → Open → `C:\FreeFinder\android` (carpeta que contiene `settings.gradle.kts`).
2. Espera la sincronización de Gradle. Hay wrapper incluido; no necesitas instalar Gradle por separado.
3. En File → Settings → Build, Execution, Deployment → Build Tools → Gradle, selecciona un JDK 17 en Gradle JDK (o Download JDK → versión 17).
4. Si `local.properties` no existe, Android Studio lo crea con la ruta del SDK de tu PC. No uses rutas del entorno de desarrollo que generó el ZIP.
5. Selecciona emulador Android 14/15 o el OnePlus Nord 4.
6. Run ▶ para compilar e instalar la variante debug.

También se puede compilar desde PowerShell en `android/`:

```powershell
.\gradlew.bat assembleDebug testDebugUnitTest
```

La APK se genera en `app\build\outputs\apk\debug\app-debug.apk`. La APK debug permite HTTP para las pruebas locales. La variante release bloquea HTTP y necesita HTTPS y firma propia.

## 5. Conectar el OnePlus Nord 4 por USB

1. En el teléfono activa opciones de desarrollador y depuración USB.
2. Conecta el cable y acepta la autorización de tu propio ordenador.
3. Ejecuta:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" devices
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" reverse tcp:8000 tcp:8000
```

4. En FreeFinder → Ajustes → URL del backend, escribe `http://127.0.0.1:8000/`.
5. Guarda los ajustes y pulsa Sincronizar catálogo en Explorar.
6. En un emulador usa `http://10.0.2.2:8000/`.

La conexión USB deja de funcionar al retirar el cable o perder la redirección ADB. Para uso permanente hace falta un backend accesible mediante HTTPS. No publiques el servidor de desarrollo directamente en Internet.

## 6. Notificación de prueba

Ajustes → Notificación de prueba → permitir notificaciones. Si habías denegado el permiso permanentemente, actívalo en Ajustes de Android → Aplicaciones → FreeFinder → Notificaciones. No se ha validado en un OnePlus físico.

## 7. Docker y PostgreSQL (opcional)

Desde la raíz del proyecto, con Docker Desktop instalado y funcionando:

```powershell
Copy-Item .env.example .env
# Edita .env: usa dos secretos diferentes, largos y seguros, preferiblemente hexadecimales.
docker compose up --build -d
```

API en http://127.0.0.1:8000 . Solo se expone a localhost. La API ejecuta las migraciones antes de estar sana; el worker espera a su healthcheck. Se comparte un bloqueo entre API y worker para evitar ejecuciones simultáneas en este despliegue de un solo host.

Para detener sin borrar datos: `docker compose down`. No uses `down -v` si quieres conservar la base de datos. Docker/PostgreSQL no se ha ejecutado aquí: se ha validado la migración con SQLite.

## 8. Copias y actualización

- Detén API y worker antes de copiar `backend\freefinder.db` si usas SQLite.
- Conserva `.env` fuera de repositorios públicos.
- Con PostgreSQL usa `pg_dump`; no copies directamente sus ficheros mientras está en marcha.
- Antes de actualizar haz copia, instala dependencias y ejecuta `python -m alembic upgrade head`.
- No ejecutes migraciones destructivas sin revisar las notas de versión.
