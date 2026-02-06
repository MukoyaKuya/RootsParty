"""
Image processing utilities using Pillow (PIL)
"""
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def crop_image(image_file, x, y, width, height, output_size=None):
    """
    Crop an image using Pillow (PIL)
    
    Args:
        image_file: Django uploaded file or file path
        x: X coordinate of crop start
        y: Y coordinate of crop start
        width: Width of crop area
        height: Height of crop area
        output_size: Optional tuple (width, height) to resize after cropping
    
    Returns:
        Cropped image as InMemoryUploadedFile
    """
    # Read image data
    if hasattr(image_file, 'read'):
        # It's a file-like object
        image_file.seek(0)  # Reset file pointer
        img = Image.open(image_file)
        # Convert to RGB if necessary (handles RGBA, P, etc.)
        if img.mode != 'RGB':
            img = img.convert('RGB')
    else:
        # It's a file path (string or Path object)
        img = Image.open(str(image_file))
        if img.mode != 'RGB':
            img = img.convert('RGB')
    
    if img is None:
        raise ValueError("Could not read image file")
    
    # Get image dimensions
    img_width, img_height = img.size
    
    # Ensure crop coordinates are within image bounds
    x = max(0, int(x))
    y = max(0, int(y))
    width = min(int(width), img_width - x)
    height = min(int(height), img_height - y)
    
    # Ensure valid dimensions
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid crop dimensions: {width}x{height}")
    
    # Crop the image (Pillow uses (left, top, right, bottom) format)
    left = x
    top = y
    right = x + width
    bottom = y + height
    
    cropped_img = img.crop((left, top, right, bottom))
    
    # Resize if output_size is specified
    if output_size:
        target_width, target_height = output_size
        # Use LANCZOS resampling for high quality
        cropped_img = cropped_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # Save to BytesIO as JPEG
    output = BytesIO()
    cropped_img.save(output, format='JPEG', quality=85, optimize=True)
    output.seek(0)
    
    # Create InMemoryUploadedFile
    filename = image_file.name if hasattr(image_file, 'name') else 'cropped.jpg'
    if '.' in filename:
        name, ext = filename.rsplit('.', 1)
        filename = f"{name}_cropped.jpg"
    else:
        filename = f"{filename}_cropped.jpg"
    
    # Get file size
    output_size_bytes = len(output.getvalue())
    output.seek(0)
    
    return InMemoryUploadedFile(
        output,
        'ImageField',
        filename,
        'image/jpeg',
        output_size_bytes,
        None
    )
