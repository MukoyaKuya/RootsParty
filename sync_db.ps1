$ErrorActionPreference = "Stop"

# Configuration
$NEON_DB_URL = "postgresql://neondb_owner:npg_JcqhweA1C8HG@ep-autumn-math-ahlr3cf2-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
$PYTHON_PATH = "C:\Users\Little Human\Desktop\RootsParty\venv\Scripts\python.exe"

Write-Host "NOTE: This script will OVERWRITE your local database with data from Neon."
Write-Host "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
Start-Sleep -Seconds 5

# Step 1: Dump data from Remote
Write-Host "`n[1/3] Dumping data from Remote (Neon)..."
$env:DATABASE_URL = $NEON_DB_URL
& $PYTHON_PATH dump_cloud_db.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to dump data."
}

# Step 2: Flush Local Database
Write-Host "`n[2/3] Flushing local database..."
$env:DATABASE_URL = "" # Unset to use local SQLite
# We need to answer "yes" to the flush prompt
echo "yes" | & $PYTHON_PATH manage.py flush
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to flush local database."
}

# Step 3: Load Data to Local
Write-Host "`n[3/3] Loading data into local SQLite..."
& $PYTHON_PATH manage.py loaddata cloud_backup.json
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to load data."
}

Write-Host "`nSUCCESS: Local database synced with Remote!"
