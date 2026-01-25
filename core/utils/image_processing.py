"""
Image processing utilities using OpenCV
"""
import cv2
import numpy as np
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def crop_image(image_file, x, y, width, height, output_size=None):
    """
    Crop an image using OpenCV
    
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
        image_data = image_file.read()
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    else:
        # It's a file path (string or Path object)
        img = cv2.imread(str(image_file))
    
    if img is None:
        raise ValueError("Could not read image file")
    
    # Convert BGR to RGB (OpenCV uses BGR by default)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Get image dimensions
    img_height, img_width = img.shape[:2]
    
    # Ensure crop coordinates are within image bounds
    x = max(0, int(x))
    y = max(0, int(y))
    width = min(int(width), img_width - x)
    height = min(int(height), img_height - y)
    
    # Crop the image
    cropped_img = img[y:y+height, x:x+width]
    
    # Resize if output_size is specified
    if output_size:
        target_width, target_height = output_size
        cropped_img = cv2.resize(cropped_img, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
    
    # Convert RGB back to BGR for encoding
    cropped_img_bgr = cv2.cvtColor(cropped_img, cv2.COLOR_RGB2BGR)
    
    # Encode image to JPEG
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
    success, encoded_img = cv2.imencode('.jpg', cropped_img_bgr, encode_param)
    
    if not success:
        raise ValueError("Failed to encode image")
    
    # Convert to bytes
    output = BytesIO(encoded_img.tobytes())
    output.seek(0)
    
    # Create InMemoryUploadedFile
    filename = image_file.name if hasattr(image_file, 'name') else 'cropped.jpg'
    if '.' in filename:
        name, ext = filename.rsplit('.', 1)
        filename = f"{name}_cropped.jpg"
    else:
        filename = f"{filename}_cropped.jpg"
    
    return InMemoryUploadedFile(
        output,
        'ImageField',
        filename,
        'image/jpeg',
        sys.getsizeof(output),
        None
    )
