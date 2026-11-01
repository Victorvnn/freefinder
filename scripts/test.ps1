Set-Location (Join-Path $PSScriptRoot '..\backend')
& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
& .\.venv\Scripts\python.exe -m pytest -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Set-Location ..\android
& .\gradlew.bat testDebugUnitTest assembleDebug
exit $LASTEXITCODE
