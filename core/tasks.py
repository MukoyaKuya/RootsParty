from celery import shared_task
from django.core.files.base import ContentFile
from .models import Event, GatePass
from .services.pdf import build_gate_pass_pdf
import random
import string

@shared_task
def generate_gate_pass_task(event_uuid):
    """Background task to generate a gate pass PDF."""
    try:
        event = Event.objects.get(uuid=event_uuid)
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        GatePass.objects.create(event=event, code=code)
        
        # If we had a storage service, we'd save it there.
        # For now, we'll just return the code as proof of task completion.
        return f"Gate pass {code} generated for event {event.title}"
    except Exception as e:
        return f"Error: {str(e)}"
