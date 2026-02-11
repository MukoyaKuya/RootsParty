import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models_splash import Splash
from django.core.files import File

optimized_path = 'media/site/splash/splash_logo_optimized.webp'

if os.path.exists(optimized_path):
    splash = Splash.get_active()
    if splash:
        print(f"Updating splash: {splash.title}")
        with open(optimized_path, 'rb') as f:
            splash.image.save('splash_logo_optimized.webp', File(f), save=True)
        print("Splash updated successfully.")
    else:
        print("No active splash found.")
else:
    print(f"Optimized file not found: {optimized_path}")
