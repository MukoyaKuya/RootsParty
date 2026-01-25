"""
Custom widgets for image cropping
"""
from django.forms.widgets import FileInput, ClearableFileInput
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.urls import reverse


class ImageCropWidget(ClearableFileInput):
    """
    Custom widget that displays an image with an interactive crop tool
    """
    template_name = 'admin/widgets/image_crop_widget.html'
    
    def __init__(self, attrs=None, crop_ratio=None, crop_width=None, crop_height=None):
        self.crop_ratio = crop_ratio
        self.crop_width = crop_width
        self.crop_height = crop_height
        super().__init__(attrs)
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['crop_ratio'] = self.crop_ratio
        context['widget']['crop_width'] = self.crop_width
        context['widget']['crop_height'] = self.crop_height
        return context
    
    def format_value(self, value):
        """Return the file object if it has a url attribute."""
        if self.is_initial(value):
            return value.url if hasattr(value, 'url') else value
        return None


class ImageCropFieldWidget(FileInput):
    """
    Widget that shows image preview with crop tool after upload
    """
    template_name = 'admin/widgets/image_crop_field.html'
    
    def __init__(self, attrs=None, crop_ratio='16/9', crop_width=800, crop_height=450):
        self.crop_ratio = crop_ratio
        self.crop_width = crop_width
        self.crop_height = crop_height
        super().__init__(attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        if value and hasattr(value, 'url'):
            image_url = value.url
        else:
            image_url = None
        
        context = {
            'name': name,
            'value': value,
            'image_url': image_url,
            'crop_ratio': self.crop_ratio,
            'crop_width': self.crop_width,
            'crop_height': self.crop_height,
            'field_id': attrs.get('id', f'id_{name}') if attrs else f'id_{name}',
        }
        
        return mark_safe(render_to_string(self.template_name, context))
