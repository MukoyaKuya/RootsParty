# CAROUSEL SETUP INSTRUCTIONS

## The Problem

The `core_carouselimage` table doesn't exist in your PostgreSQL database because the migration hasn't been applied yet.

## Quick Fix - Copy and Paste These Commands

Open a **NEW** PowerShell terminal (not the one running the server) and run these commands **one by one**:

```powershell
# Step 1: Navigate to project
cd "C:\Users\Little Human\Desktop\RootsParty"

# Step 2: Activate virtual environment
.\venv\Scripts\Activate.ps1

# Step 3: Run the migration
python manage.py migrate core

# Step 4: Populate carousel with images
python manage.py populate_carousel
```

## If That Doesn't Work

Try this alternative:

```powershell
cd "C:\Users\Little Human\Desktop\RootsParty"
.\venv\Scripts\python.exe manage.py migrate core
.\venv\Scripts\python.exe manage.py populate_carousel
```

## Or Use the Python Scripts I Created

```powershell
cd "C:\Users\Little Human\Desktop\RootsParty"
.\venv\Scripts\python.exe apply_carousel_migration.py
.\venv\Scripts\python.exe populate_carousel_data.py
```

## What Should Happen

When the migration runs successfully, you'll see:

```
Running migrations:
  Applying core.0028_carouselimage... OK
```

Then when you populate the carousel:

```
✅ Created: Roots Party Movement
✅ Created: Economic Liberation
✅ Created: Youth Empowerment
```

## After Success

1. Refresh http://localhost:8080/admin/core/carouselimage/
2. You should see the carousel admin page
3. Visit http://localhost:8080/ to see the carousel on the homepage

## Files I Created

- `core/migrations/0028_carouselimage.py` - The migration file
- `apply_carousel_migration.py` - Script to run migration
- `populate_carousel_data.py` - Script to add default images
- `setup_carousel.bat` - Batch file (double-click in File Explorer)

## Still Having Issues?

The migration file exists at: `core/migrations/0028_carouselimage.py`

You just need to apply it to your database. The command is simply:

```
python manage.py migrate
```

This will create the `core_carouselimage` table in your PostgreSQL database.
