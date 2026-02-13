from django import template
from django.conf import settings
from image_cropping.templatetags.cropping import cropped_thumbnail
import logging

register = template.Library()
logger = logging.getLogger(__name__)

@register.simple_tag(takes_context=True)
def safe_cropped_thumbnail(context, instance, ratio_fieldname, scale=1):
    """
    Safely renders a cropped thumbnail.
    If the cropping data is invalid (e.g. filename string instead of coordinates),
    it falls back to a standard thumbnail of the source image.
    """
    try:
        # Try the standard cropped_thumbnail tag logic
        return cropped_thumbnail(context, instance, ratio_fieldname, scale)
    except (ValueError, AttributeError, TypeError) as e:
        # Log the error for debugging
        logger.warning(f"Invalid cropping data for {instance}: {e}")
        
        # Fallback: Validation failed, return original image URL or standard thumbnail
        # We can try to use easy_thumbnails directly to just resize
        try:
            from easy_thumbnails.files import get_thumbnailer
            
            # get the source image field
            image_field = getattr(instance, 'image', None)
            if not image_field:
                return ''
                
            # Parse the ratio field to get dimensions, e.g. "800x450"
            # The field on the model is an ImageRatioField
            # We need to look up the field definition to get the size
            # But simpler fallback is just to use the original image url
            # or a standard size if we know it.
            
            # For now, let's just return the original URL which is safe
            return image_field.url
            
        except Exception as e2:
             logger.error(f"Fallback failed for {instance}: {e2}")
             return ''
