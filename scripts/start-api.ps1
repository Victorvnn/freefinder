$ErrorActionPreference='Stop'
Set-Location (Join-Path $PSScriptRoot '..\backend')
& .\.venv\Scripts\python.exe run_api.py
