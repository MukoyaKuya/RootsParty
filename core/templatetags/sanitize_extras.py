import bleach
from django import template
from django.utils.safestring import mark_safe


register = template.Library()

ALLOWED_TAGS = [
    'a', 'abbr', 'b', 'blockquote', 'br', 'code', 'div', 'em', 'h1', 'h2', 'h3',
    'h4', 'h5', 'h6', 'hr', 'i', 'li', 'ol', 'p', 'pre', 'span', 'strong',
    'table', 'tbody', 'td', 'th', 'thead', 'tr', 'ul',
]

ALLOWED_ATTRIBUTES = {
    '*': ['class'],
    'a': ['href', 'rel', 'target', 'title'],
    'abbr': ['title'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan', 'scope'],
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


@register.filter
def sanitize_html(value):
    cleaned = bleach.clean(
        value or '',
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    return mark_safe(cleaned)
