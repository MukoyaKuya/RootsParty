from PIL import Image
import os

def resize_logo():
    logo_path = r'c:\Users\Little Human\Desktop\RootsParty\static\images\logo.png'
    backup_path = r'c:\Users\Little Human\Desktop\RootsParty\static\images\logo_backup.png'

    if not os.path.exists(logo_path):
        print(f"Error: {logo_path} not found.")
        return

    # Create backup
    if not os.path.exists(backup_path):
        img_backup = Image.open(logo_path)
        img_backup.save(backup_path)
        print(f"Backup created at {backup_path}")

    # Resize
    with Image.open(logo_path) as img:
        print(f"Original size: {img.size}")
        if img.size[0] > 256:
            new_size = (256, 256)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            img.save(logo_path, optimize=True)
            print(f"Resized image saved to {logo_path}. New size: {img.size}")
        else:
            print("Image is already small enough.")

if __name__ == "__main__":
    resize_logo()
