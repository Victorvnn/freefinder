$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..\backend')
py -3 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Instala Python 3.12 o superior y el Python Launcher.' }
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias.' }
if (!(Test-Path .env)) {
  $token = & .\.venv\Scripts\python.exe -c 'import secrets; print(secrets.token_hex(32))'
  "DATABASE_URL=sqlite:///./freefinder.db`nADMIN_TOKEN=$token`nSCAN_HOURS=6`nLOCK_FILE=./freefinder-worker.lock" | Set-Content -Encoding utf8 .env
}
& .\.venv\Scripts\python.exe -m alembic upgrade head
if ($LASTEXITCODE -ne 0) { throw 'Error de migración. Consulta la documentación; no borres bases existentes.' }
Write-Host 'Instalado. Ejecuta start-api.ps1 y start-worker.ps1 en dos terminales.'
