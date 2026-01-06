
from django.utils.html import format_html
try:
    format_html("<b>test</b>")
except TypeError as e:
    print(f"Caught expected error: {e}")

from django.utils.safestring import mark_safe
print(f"mark_safe works: {mark_safe('<b>test</b>')}")
