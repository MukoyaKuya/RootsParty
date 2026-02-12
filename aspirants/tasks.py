from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import AspirantRegistration
from .services import build_aspirant_profile_pdf, build_aspirants_report_pdf

@shared_task
def generate_aspirant_profile_pdf_task(aspirant_uuid):
    """Generate and save the profile PDF for a single aspirant."""
    try:
        aspirant = AspirantRegistration.objects.get(uuid=aspirant_uuid)
        buffer = build_aspirant_profile_pdf(aspirant)
        
        filename = f"Profile_{aspirant.surname}_{aspirant.id_number}.pdf"
        aspirant.profile_pdf.save(filename, ContentFile(buffer.read()), save=True)
        
        return f"Profile PDF generated for {aspirant.surname} (ID: {aspirant.id_number})"
    except Exception as e:
        return f"Error generating aspirant profile PDF: {str(e)}"

@shared_task
def generate_aspirants_report_pdf_task(report_id):
    """
    Generate the full aspirants report and save to PartyReport.
    """
    try:
        from core.models import PartyReport
        report = PartyReport.objects.get(id=report_id)
        
        buffer = build_aspirants_report_pdf()
        
        filename = f"Roots_Aspirants_Report_{timezone.now().strftime('%Y%m%d')}.pdf"
        report.pdf_file.save(filename, ContentFile(buffer.read()), save=True)
        
        return f"Aspirants report #{report_id} generated successfully."
    except Exception as e:
        return f"Error generating aspirants list PDF: {str(e)}"
