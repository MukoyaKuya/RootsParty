from PIL import Image
import os

logos = ['logo-192.png', 'logo-512.png', 'logo.png']
base_dir = r'c:\Users\Little Human\Desktop\RootsParty\static\images'

print(f"Checking images in {base_dir}...")
for name in logos:
    path = os.path.join(base_dir, name)
    if not os.path.exists(path):
        print(f"MISSING: {name}")
        continue
        
    try:
        img = Image.open(path)
        print(f"\nImage: {name}")
        print(f"  Format: {img.format}")
        print(f"  Mode: {img.mode}")
        print(f"  Size: {img.size}")
        
        if img.mode == 'RGBA':
            # Check if it actually has transparency
            extrema = img.getextrema()
            if extrema[3][0] < 255:
                print("  Status: Has TRANSPARENCY (Alpha channel < 255)")
            else:
                print("  Status: RGBA but verify opaque")
        elif img.mode == 'P':
             print(f"  Status: Palette mode (transparency info: {img.info.get('transparency')})")
        else:
            print("  Status: Opaque (No Alpha)")
            
    except Exception as e:
        print(f"  Error: {e}")
