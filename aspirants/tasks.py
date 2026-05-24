import logging
from django.core.files.base import ContentFile
from django.utils import timezone
from core.utils.tasking import shared_task
from .models import AspirantRegistration
from .services import build_aspirant_profile_pdf, build_aspirants_report_pdf

logger = logging.getLogger(__name__)

@shared_task(autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def generate_aspirant_profile_pdf_task(aspirant_uuid):
    """Generate and save the profile PDF for a single aspirant."""
    try:
        aspirant = AspirantRegistration.objects.get(uuid=aspirant_uuid)
        if aspirant.profile_pdf:
            return f"Profile PDF already exists for {aspirant.surname} (ID: {aspirant.id_number})"
        buffer = build_aspirant_profile_pdf(aspirant)
        
        filename = f"Profile_{aspirant.surname}_{aspirant.id_number}.pdf"
        aspirant.profile_pdf.save(filename, ContentFile(buffer.read()), save=True)
        
        return f"Profile PDF generated for {aspirant.surname} (ID: {aspirant.id_number})"
    except Exception as e:
        logger.exception("Error generating aspirant profile PDF for %s", aspirant_uuid)
        raise

@shared_task(autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def generate_aspirants_report_pdf_task(report_id):
    """
    Generate the full aspirants report and save to PartyReport.
    """
    try:
        from core.models import PartyReport
        report = PartyReport.objects.get(id=report_id)
        if report.pdf_file:
            return f"Aspirants report #{report_id} already exists."
        
        buffer = build_aspirants_report_pdf()
        
        filename = f"Roots_Aspirants_Report_{timezone.now().strftime('%Y%m%d')}.pdf"
        report.pdf_file.save(filename, ContentFile(buffer.read()), save=True)
        
        return f"Aspirants report #{report_id} generated successfully."
    except Exception as e:
        logger.exception("Error generating aspirants list PDF for report %s", report_id)
        raise
