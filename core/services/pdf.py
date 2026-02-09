"""
PDF generation services for core app.
Keeps PDF building logic out of views for testability and reuse.
"""
import io
import os

import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfgen import canvas

from django.conf import settings
from django.contrib.staticfiles import finders


def _draw_wrapped_text(c, text, x, y, max_width, font_name, font_size, leading=None):
    """Draw centred text with wrapping; return new Y position."""
    if leading is None:
        leading = font_size * 1.2
    c.setFont(font_name, font_size)
    lines = simpleSplit(text, font_name, font_size, max_width)
    for line in lines:
        c.drawCentredString(x, y, line)
        y -= leading
    return y


def build_gate_pass_pdf(event, code):
    """
    Build the gate pass PDF for an event with the given access code.
    Caller is responsible for creating the GatePass record and updating Event stats.

    Args:
        event: Event instance (must have title, location, date, slug, id).
        code: str – access code to render on the PDF (and in QR).

    Returns:
        io.BytesIO buffer containing the PDF (positioned at 0).
    """
    buffer = io.BytesIO()
    width, height = A4
    p = canvas.Canvas(buffer, pagesize=A4)

    # 1. Background / Border
    p.setStrokeColor(colors.black)
    p.setLineWidth(5)
    p.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

    # 2. Header
    current_y = height - 1.0 * inch
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 30)
    p.drawCentredString(width / 2, current_y, "ROOTS PARTY")
    current_y -= 0.35 * inch
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, current_y, "TINGIZA MTI!")

    # 3. Logo
    current_y -= 1.8 * inch
    logo_size = 1.6 * inch
    logo_y = current_y + 0.1 * inch
    try:
        logo_path = finders.find('images/roots_logo_circle.png')
        if logo_path and os.path.exists(logo_path):
            logo_x = (width - logo_size) / 2
            p.drawImage(logo_path, logo_x, logo_y, width=logo_size, height=logo_size, mask='auto', preserveAspectRatio=True)
    except Exception:
        pass

    # 4. "OFFICIAL GATE PASS"
    current_y -= 0.6 * inch
    p.setFillColor(colors.red)
    p.setFont("Helvetica-Bold", 28)
    p.drawCentredString(width / 2, current_y, "OFFICIAL GATE PASS")

    # 5. Event details
    current_y -= 0.8 * inch
    p.setFillColor(colors.black)
    current_y = _draw_wrapped_text(p, event.title.upper(), width / 2, current_y, width - 2 * inch, "Helvetica-Bold", 22)
    current_y -= 0.5 * inch
    p.setFont("Helvetica", 16)
    p.drawCentredString(width / 2, current_y, f"LOCATION: {event.location.upper()}")
    current_y -= 0.35 * inch
    p.drawCentredString(width / 2, current_y, f"DATE: {event.date.strftime('%d %B %Y').upper()}")
    current_y -= 0.3 * inch
    p.drawCentredString(width / 2, current_y, f"TIME: {event.date.strftime('%H:%M')}")

    # 6. Access code
    current_y -= 0.8 * inch
    p.setFont("Courier-Bold", 24)
    p.setFillColor(colors.HexColor('#1a1a1a'))
    p.drawCentredString(width / 2, current_y, f"CODE: {code}")

    # 7. QR code
    qr_size = 2.4 * inch
    qr_y = 1.6 * inch
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(f"ROOTSPARTY-EVENT-{event.id}-{code}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = io.BytesIO()
    img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    p.drawImage(ImageReader(qr_buffer), (width - qr_size) / 2, qr_y, width=qr_size, height=qr_size)

    # Footer
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Oblique", 12)
    p.drawCentredString(width / 2, 1.0 * inch, "Admit One. Non-Transferable. Tingiza Mti.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
