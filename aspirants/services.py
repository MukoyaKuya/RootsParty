"""
PDF generation services for the aspirants app.
Keeps PDF building logic out of views for testability and reuse.
"""
import io
import os
import urllib.request

from django.conf import settings
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    Image as ReportLabImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .models import AspirantRegistration


def _logo_path(size='small'):
    """Return path to Roots logo for PDFs. size: 'small' (80px) or 'large' (150px)."""
    static_dirs = getattr(settings, 'STATICFILES_DIRS', None) or []
    if static_dirs:
        path = os.path.join(static_dirs[0], 'images', 'roots_logo_circle.png')
        if os.path.exists(path):
            return path
    root = getattr(settings, 'STATIC_ROOT', None)
    if root:
        path = os.path.join(root, 'images', 'roots_logo_circle.png')
        if os.path.exists(path):
            return path
    return None


def build_aspirant_profile_pdf(aspirant):
    """
    Build the official aspirant profile PDF for a single AspirantRegistration.

    Args:
        aspirant: AspirantRegistration instance.

    Returns:
        io.BytesIO buffer containing the PDF (positioned at 0).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title=f"Aspirant Profile - {aspirant.surname}",
    )
    elements = []
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='HeaderTitle', parent=styles['Heading1'],
        alignment=TA_CENTER, fontSize=24, spaceAfter=10, textColor=colors.HexColor('#1a1a1a'),
    ))
    styles.add(ParagraphStyle(
        name='HeaderSubtitle', parent=styles['Normal'],
        alignment=TA_CENTER, fontSize=14, spaceAfter=20, textColor=colors.HexColor('#d32f2f'), fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        name='SectionHeader', parent=styles['Heading2'],
        fontSize=16, spaceBefore=15, spaceAfter=10, textColor=colors.HexColor('#1a1a1a'),
        borderPadding=5, borderColor=colors.HexColor('#1a1a1a'), borderWidth=0, borderBottomWidth=2,
    ))
    styles.add(ParagraphStyle(name='Label', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#555555')))
    styles.add(ParagraphStyle(name='Value', parent=styles['Normal'], fontSize=11, fontName='Helvetica', textColor=colors.black))
    styles.add(ParagraphStyle(name='FooterText', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.gray))

    logo_path = _logo_path('small')
    if logo_path:
        im = ReportLabImage(logo_path, width=80, height=80)
        im.hAlign = 'CENTER'
        elements.append(im)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("ROOTS PARTY OF KENYA", styles['HeaderTitle']))
    elements.append(Paragraph("OFFICIAL ASPIRANT PROFILE", styles['HeaderSubtitle']))
    elements.append(Spacer(1, 10))

    photo_img = None
    if aspirant.photo and hasattr(aspirant.photo, 'path') and os.path.exists(aspirant.photo.path):
        try:
            photo_img = ReportLabImage(aspirant.photo.path, width=150, height=150)
            photo_img.hAlign = 'RIGHT'
        except Exception:
            photo_img = Paragraph("[Photo Error]", styles['Normal'])
    else:
        photo_img = Paragraph("NO PHOTO", styles['Normal'])

    verified_text = "Pending Verification"
    verified_color = "red"
    if aspirant.is_verified:
        verified_text = "VERIFIED"
        verified_color = "green"

    basic_info_data = [
        [Paragraph("Application ID:", styles['Label']), Paragraph(f"#{aspirant.id}", styles['Value'])],
        [Paragraph("Date Submitted:", styles['Label']), Paragraph(aspirant.created_at.strftime('%d %B %Y'), styles['Value'])],
        [Paragraph("Status:", styles['Label']), Paragraph(aspirant.get_status_display().upper(), styles['Value'])],
        [Paragraph("Verification:", styles['Label']), Paragraph(f"<font color='{verified_color}'><b>{verified_text}</b></font>", styles['Value'])],
        [Paragraph("Position:", styles['Label']), Paragraph(aspirant.get_position_display().upper(), styles['Value'])],
    ]
    basic_info_table = Table(basic_info_data, colWidths=[120, 200])
    basic_info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    header_table_data = [[basic_info_table, photo_img]]
    header_table = Table(header_table_data, colWidths=[350, 160])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("PERSONAL DETAILS", styles['SectionHeader']))
    details_data = [
        [Paragraph("Surname:", styles['Label']), Paragraph(aspirant.surname, styles['Value'])],
        [Paragraph("Other Names:", styles['Label']), Paragraph(aspirant.other_names, styles['Value'])],
        [Paragraph("ID Number:", styles['Label']), Paragraph(aspirant.id_number, styles['Value'])],
        [Paragraph("Date of Birth:", styles['Label']), Paragraph(aspirant.date_of_birth.strftime('%d %B %Y') if aspirant.date_of_birth else "-", styles['Value'])],
        [Paragraph("Phone Number:", styles['Label']), Paragraph(aspirant.phone_number, styles['Value'])],
        [Paragraph("Email Address:", styles['Label']), Paragraph(aspirant.email or "-", styles['Value'])],
    ]
    if aspirant.is_incumbent:
        details_data.append([Paragraph("Incumbent:", styles['Label']), Paragraph("Yes, currently elected", styles['Value'])])
    details_data.append([Paragraph("Membership Status:", styles['Label']), Paragraph(aspirant.get_membership_status_display(), styles['Value'])])
    details_data.append([Paragraph("Payment Status:", styles['Label']), Paragraph(aspirant.get_payment_status_display(), styles['Value'])])

    details_table = Table(details_data, colWidths=[180, 330])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f9fafb')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 30))

    elements.append(Paragraph("DECLARATION", styles['SectionHeader']))
    declaration_text = (
        f"I, <b>{aspirant.surname} {aspirant.other_names}</b>, confirmed that the information provided is accurate and complete. "
        f"I achieved this by accepting the Terms and Conditions of Roots Party of Kenya during the registration process on {aspirant.created_at.strftime('%d %B %Y')}."
    )
    elements.append(Paragraph(declaration_text, styles['Normal']))
    elements.append(Spacer(1, 40))

    sig_data = [
        ["__________________________", "__________________________"],
        ["Signature", "Party Official / Date"],
    ]
    sig_table = Table(sig_data, colWidths=[250, 250])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Oblique'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
    ]))
    elements.append(sig_table)

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.gray)
        canvas.drawString(40, 30, f"Generated on {timezone.now().strftime('%d %B %Y %H:%M')}")
        canvas.drawCentredString(A4[0] / 2, 30, "Roots Party of Kenya - Internal Document")
        canvas.drawRightString(A4[0] - 40, 30, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    return buffer


def _report_photo_cell(asp):
    """Build photo cell for report table (image or empty)."""
    if not asp.photo:
        return ""
    try:
        if hasattr(asp.photo, 'path') and os.path.exists(asp.photo.path):
            return ReportLabImage(asp.photo.path, width=30, height=30)
    except (NotImplementedError, FileNotFoundError, AttributeError):
        pass
    try:
        if asp.photo.url:
            with urllib.request.urlopen(asp.photo.url, timeout=5) as response:
                image_data = response.read()
                return ReportLabImage(io.BytesIO(image_data), width=30, height=30)
    except Exception:
        pass
    return ""


def _report_jurisdiction(asp):
    """Format jurisdiction string for report row."""
    if asp.position in ['governor', 'senator', 'woman_rep']:
        return asp.county.name if asp.county else "-"
    if asp.position == 'mp':
        return f"{asp.constituency}, {asp.county.name}" if asp.county else asp.constituency or "-"
    if asp.position == 'mca':
        return f"{asp.county.name}, {asp.ward} Ward, {asp.constituency} North" if asp.county else f"{asp.ward}, {asp.constituency}"
    if asp.position == 'president':
        return "National"
    return ""


def build_aspirants_report_pdf():
    """
    Build the full aspirants registration report PDF (all applications grouped by position).

    Returns:
        io.BytesIO buffer containing the PDF (positioned at 0).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
        title="Roots Party - Aspirant Report",
    )
    elements = []
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='CoverTitle', parent=styles['Heading1'],
        alignment=TA_CENTER, fontSize=30, leading=36, spaceAfter=20,
        textColor=colors.HexColor('#1a1a1a'), fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        name='CoverSubtitle', parent=styles['Heading2'],
        alignment=TA_CENTER, fontSize=18, leading=24, spaceAfter=10,
        textColor=colors.HexColor('#d32f2f'), fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(name='CoverDate', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, textColor=colors.HexColor('#555555')))
    styles.add(ParagraphStyle(name='CoverStats', parent=styles['Normal'], alignment=TA_CENTER, fontSize=14, textColor=colors.HexColor('#1a1a1a'), spaceBefore=30))
    styles.add(ParagraphStyle(name='PositionHeader', parent=styles['Heading2'], fontSize=14, spaceBefore=15, spaceAfter=10, textColor=colors.HexColor('#d32f2f'), borderPadding=5, borderBottomWidth=1, borderColor=colors.HexColor('#d32f2f')))
    styles.add(ParagraphStyle(name='TableHeader', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold', textColor=colors.black, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='TableBody', parent=styles['Normal'], fontSize=8, fontName='Helvetica', alignment=TA_LEFT))

    elements.append(Spacer(1, 60))
    logo_path = _logo_path('large')
    if logo_path:
        im = ReportLabImage(logo_path, width=150, height=150)
        im.hAlign = 'CENTER'
        elements.append(im)
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("ROOTS PARTY OF KENYA", styles['CoverTitle']))
    elements.append(Paragraph("ASPIRANT REGISTRATION REPORT", styles['CoverSubtitle']))
    line_data = [[""]]
    line_table = Table(line_data, colWidths=[400])
    line_table.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#d32f2f')),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Generated on {timezone.now().strftime('%d %B %Y')}", styles['CoverDate']))
    elements.append(Paragraph(f"at {timezone.now().strftime('%H:%M')}", styles['CoverDate']))
    elements.append(Spacer(1, 50))

    total_aspirants = AspirantRegistration.objects.count()
    elements.append(Paragraph(f"Total Applications Received: <b>{total_aspirants}</b>", styles['CoverStats']))
    elements.append(PageBreak())

    position_order = ['president', 'governor', 'senator', 'woman_rep', 'mp', 'mca']
    position_labels = dict(AspirantRegistration.POSITION_CHOICES)

    for pos_key in position_order:
        aspirants = AspirantRegistration.objects.select_related('county').filter(position=pos_key).order_by('surname')
        if not aspirants.exists():
            continue
        pos_label = position_labels.get(pos_key, pos_key.replace('_', ' ').title())
        elements.append(Paragraph(f"{pos_label} ({aspirants.count()})", styles['PositionHeader']))

        data = [[
            Paragraph("Photo", styles['TableHeader']),
            Paragraph("Particulars", styles['TableHeader']),
            Paragraph("Jurisdiction", styles['TableHeader']),
            Paragraph("Phone No", styles['TableHeader']),
            Paragraph("Seat", styles['TableHeader']),
            Paragraph("Status", styles['TableHeader']),
        ]]
        for asp in aspirants:
            photo_cell = _report_photo_cell(asp)
            jurisdiction = _report_jurisdiction(asp)
            verified_mark = " <font color='green' size=8>[VERIFIED]</font>" if asp.is_verified else ""
            status_cell = f"{verified_mark}<br/>{asp.get_status_display()}" if asp.is_verified else asp.get_status_display()
            data.append([
                photo_cell,
                Paragraph(f"<b>{asp.surname}</b>, {asp.other_names}<br/><font size=7>ID: {asp.id_number}</font>", styles['TableBody']),
                Paragraph(jurisdiction, styles['TableBody']),
                Paragraph(asp.phone_number, styles['TableBody']),
                Paragraph(asp.get_position_display().upper(), styles['TableBody']),
                Paragraph(status_cell, styles['TableBody']),
            ])
        t = Table(data, colWidths=[45, 165, 140, 85, 65, 85])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (1, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#9ca3af')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 15))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.gray)
        canvas.drawString(30, 20, "Roots Party of Kenya | Confidential Internal Report")
        canvas.drawRightString(A4[0] - 30, 20, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    return buffer
