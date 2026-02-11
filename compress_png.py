from PIL import Image
import os

img_path = 'media/site/splash/lumina-enhanced-1770792077328.png'
output_path = 'media/site/splash/splash_logo_optimized.png'

if os.path.exists(img_path):
    with Image.open(img_path) as img:
        # Resize to 1200px max (still 3x larger than before for "high quality")
        max_width = 1200
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Save as PNG with optimization
        img.save(output_path, 'PNG', optimize=True)
        print(f"Optimized PNG: {output_path}, {os.path.getsize(output_path)} bytes")
