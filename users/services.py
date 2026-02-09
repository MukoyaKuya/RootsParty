"""
Services for the users app (e.g. PDF generation).
"""
import io
import os

from django.conf import settings


def build_member_card_pdf(member):
    """
    Build the membership card PDF for a member (credit-card size).
    Requires: qrcode, reportlab, PIL.

    Args:
        member: Member instance (must have id, full_name, id_number, county).

    Returns:
        io.BytesIO buffer containing the PDF (positioned at 0).

    Raises:
        ImportError: If qrcode or reportlab is not installed.
    """
    import qrcode
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    card_width = 3.375 * inch
    card_height = 2.125 * inch
    c = canvas.Canvas(buffer, pagesize=(card_width, card_height))

    roots_red = colors.HexColor('#E60000')
    roots_black = colors.HexColor('#1a1a1a')

    # Background
    c.setFillColor(colors.white)
    c.rect(0, 0, card_width, card_height, fill=1, stroke=0)

    # Red header stripe
    header_height = 0.6 * inch
    c.setFillColor(roots_red)
    c.rect(0, card_height - header_height, card_width, header_height, fill=1, stroke=0)

    # Header text
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.15 * inch, card_height - 0.3 * inch, "ROOTS PARTY")
    c.setFont("Helvetica-Bold", 7)
    c.drawString(0.15 * inch, card_height - 0.45 * inch, "OFFICIAL MEMBERSHIP CARD")

    # Party logo
    try:
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'roots_logo_circle.png')
        if not os.path.exists(logo_path) and getattr(settings, 'STATICFILES_DIRS', None):
            logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'images', 'roots_logo_circle.png')
        if os.path.exists(logo_path):
            logo_size = 0.5 * inch
            logo_x = card_width - logo_size - 0.15 * inch
            logo_y = card_height - header_height + (header_height - logo_size) / 2
            c.drawImage(logo_path, logo_x, logo_y, width=logo_size, height=logo_size, mask='auto')
    except Exception:
        pass

    # Member info section
    y_pos = card_height - header_height - 0.2 * inch

    # Member ID badge
    badge_width = 0.8 * inch
    badge_height = 0.25 * inch
    c.setFillColor(roots_black)
    c.rect(0.15 * inch, y_pos - badge_height, badge_width, badge_height, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(0.15 * inch + badge_width / 2, y_pos - 0.09 * inch, "MEMBER")
    c.setFillColor(roots_red)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(0.15 * inch + badge_width / 2, y_pos - 0.2 * inch, f"#{member.id}")

    y_pos -= 0.4 * inch

    # Name
    c.setFillColor(colors.HexColor('#666666'))
    c.setFont("Helvetica-Bold", 5)
    c.drawString(0.15 * inch, y_pos, "NAME")
    y_pos -= 0.12 * inch
    c.setFillColor(roots_black)
    c.setFont("Helvetica-Bold", 10)
    name = member.full_name.upper()
    if len(name) > 20:
        name = name[:20] + "..."
    c.drawString(0.15 * inch, y_pos, name)

    y_pos -= 0.25 * inch

    # ID Number
    c.setFillColor(colors.HexColor('#666666'))
    c.setFont("Helvetica-Bold", 5)
    c.drawString(0.15 * inch, y_pos, "NATIONAL ID")
    y_pos -= 0.12 * inch
    c.setFillColor(roots_black)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(0.15 * inch, y_pos, str(member.id_number))

    y_pos -= 0.25 * inch

    # County
    if member.county:
        c.setFillColor(colors.HexColor('#666666'))
        c.setFont("Helvetica-Bold", 5)
        c.drawString(0.15 * inch, y_pos, "COUNTY")
        y_pos -= 0.12 * inch
        c.setFillColor(roots_black)
        c.setFont("Helvetica-Bold", 8)
        county_name = member.county.name.upper()
        if len(county_name) > 15:
            county_name = county_name[:15] + "..."
        c.drawString(0.15 * inch, y_pos, county_name)

    # QR code
    qr_data = f"MEMBER_ID:{member.id}|ID:{member.id_number}|NAME:{member.full_name}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    qr_size = 1.1 * inch
    qr_x = card_width - qr_size - 0.15 * inch
    qr_y = 0.25 * inch

    c.setFillColor(colors.HexColor('#f5f5f5'))
    c.setStrokeColor(roots_black)
    c.setLineWidth(2)
    c.rect(qr_x - 0.05 * inch, qr_y - 0.05 * inch,
           qr_size + 0.1 * inch, qr_size + 0.1 * inch,
           fill=1, stroke=1)
    c.drawImage(ImageReader(qr_buffer), qr_x, qr_y, width=qr_size, height=qr_size, mask='auto')

    c.setFillColor(roots_black)
    c.setFont("Helvetica-Bold", 5)
    c.drawCentredString(qr_x + qr_size / 2, qr_y - 0.12 * inch, "SCAN TO VERIFY")

    # Footer
    c.setFillColor(roots_black)
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(card_width / 2, 0.08 * inch, "TINGIZA MTI")

    # Border
    c.setStrokeColor(roots_black)
    c.setLineWidth(3)
    c.rect(0, 0, card_width, card_height, fill=0, stroke=1)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
