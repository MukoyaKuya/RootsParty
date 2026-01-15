@echo off
echo ============================================================
echo Running Carousel Migration
echo ============================================================
"C:\Users\Little Human\Desktop\RootsParty\venv\Scripts\python.exe" "C:\Users\Little Human\Desktop\RootsParty\apply_carousel_migration.py"

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo Migration successful! Now populating carousel...
    echo ============================================================
    "C:\Users\Little Human\Desktop\RootsParty\venv\Scripts\python.exe" "C:\Users\Little Human\Desktop\RootsParty\populate_carousel_data.py"
) else (
    echo.
    echo Migration failed! Please check the error above.
)

echo.
echo Press any key to exit...
pause >nul
