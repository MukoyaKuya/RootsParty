from PIL import Image
import os

img_path = 'media/site/splash/lumina-enhanced-1770792077328.png'
output_path = 'media/site/splash/splash_logo_optimized.webp'

if os.path.exists(img_path):
    with Image.open(img_path) as img:
        print(f"Original: {img.format}, {img.size}, {os.path.getsize(img_path)} bytes")
        
        # Resize if extremely large (e.g., > 1200px)
        max_width = 800
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            print(f"Resized to: {img.size}")
            
        # Convert to WebP for maximum efficiency
        img.save(output_path, 'WEBP', quality=85, method=6)
        print(f"Optimized: {output_path}, {os.path.getsize(output_path)} bytes")
else:
    print(f"File not found: {img_path}")
