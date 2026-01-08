from PIL import Image
import os

base_dir = r'c:\Users\Little Human\Desktop\RootsParty\static\images'
source_path = os.path.join(base_dir, 'logo.png') # This is the good one with real transparency
target_sizes = [192, 512]

if not os.path.exists(source_path):
    print("Error: Source logo.png not found!")
    exit(1)

print(f"Loading source: {source_path}")
source_img = Image.open(source_path)

if source_img.mode != 'RGBA':
    print("Warning: Source is not RGBA, converting...")
    source_img = source_img.convert('RGBA')

for size in target_sizes:
    filename = f"logo-{size}.png"
    target_path = os.path.join(base_dir, filename)
    
    print(f"\nProcessing {filename}...")
    
    # Resize with high quality (LANCZOS)
    # Using 'thumbnail' to preserve aspect ratio if needed, but here we want exact square
    # First resize while keeping aspect ratio
    img_copy = source_img.copy()
    img_copy.thumbnail((size, size), Image.Resampling.LANCZOS)
    
    # Create white canvas
    new_img = Image.new("RGB", (size, size), (255, 255, 255))
    
    # Calculate position to center
    pos_x = (size - img_copy.width) // 2
    pos_y = (size - img_copy.height) // 2
    
    # Paste the resized logo onto the white canvas using alpha as mask
    new_img.paste(img_copy, (pos_x, pos_y), mask=img_copy)
    
    # Save as PNG
    new_img.save(target_path, "PNG")
    print(f"Saved {target_path} (Size: {size}x{size}, Background: White)")

print("\nDone! PWA icons updated with white background.")
