# PowerShell script to run carousel migration
$pythonPath = "C:\Users\Little Human\Desktop\RootsParty\venv\Scripts\python.exe"
$scriptPath = "C:\Users\Little Human\Desktop\RootsParty\apply_carousel_migration.py"

Write-Host "Running migration..." -ForegroundColor Green
& $pythonPath $scriptPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nMigration successful! Now populating carousel..." -ForegroundColor Green
    $populateScript = "C:\Users\Little Human\Desktop\RootsParty\populate_carousel_data.py"
    & $pythonPath $populateScript
}
