import logging
from django.core.files.base import ContentFile
from django.db.models import F
from core.utils.tasking import shared_task
from .models import Event, GatePass
from .services.pdf import build_gate_pass_pdf
import random
import string

logger = logging.getLogger(__name__)

@shared_task(autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def generate_gate_pass_task(gate_pass_id):
    """Background task to generate and save a gate pass PDF for an existing GatePass."""
    try:
        gate_pass = GatePass.objects.get(id=gate_pass_id)
        if gate_pass.pdf_file:
            return f"Gate pass {gate_pass.code} already exists"
        event = gate_pass.event
        code = gate_pass.code
        
        # Build the PDF buffer
        buffer = build_gate_pass_pdf(event, code)
        
        # Save PDF to existing gate_pass
        filename = f"gate_pass_{event.slug}_{code}.pdf"
        gate_pass.pdf_file.save(filename, ContentFile(buffer.read()), save=True)
        
        # Update event stats
        Event.objects.filter(pk=event.pk).update(gate_pass_downloads=F('gate_pass_downloads') + 1)
        
        return f"Gate pass {code} generated and saved for event {event.title}"
    except Exception as e:
        logger.exception("Error generating gate pass %s", gate_pass_id)
        raise
