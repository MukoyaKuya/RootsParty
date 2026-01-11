from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Member
from django.db import IntegrityError, transaction
import random
from datetime import datetime
from django.contrib.auth.decorators import user_passes_test

from core.models import County

# Optional imports for membership card generation
try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch, mm
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader
    QRCODE_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: Card generation libraries not available: {e}")
    QRCODE_AVAILABLE = False
    
import io
import os
from django.conf import settings

def join(request):
    if request.method == "POST":
        # Personal Info
        surname = request.POST.get('surname')
        other_names = request.POST.get('other_names')
        full_name = f"{surname} {other_names}".strip() # Fallback for backward compatibility
        id_number = request.POST.get('id_number')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        date_of_birth = request.POST.get('date_of_birth')
        
        # Demographics
        occupation = request.POST.get('occupation')
        ethnicity = request.POST.get('ethnicity')
        sex = request.POST.get('sex')
        special_interest = request.POST.get('special_interest')
        
        # Location
        county_id = request.POST.get('county')
        constituency = request.POST.get('constituency')
        ward = request.POST.get('ward')
        polling_center = request.POST.get('polling_center')

        # Basic validation
        if not id_number or not phone or not surname:
            messages.error(request, 'Please fill all required fields')
            counties = County.objects.all().order_by('name')
            return render(request, 'users/join.html', {'counties': counties})
            
        try:
            # Get County object if selected
            county_obj = None
            if county_id:
                try:
                    county_obj = County.objects.get(id=county_id)
                except County.DoesNotExist:
                    pass

            member = Member.objects.create(
                full_name=full_name,
                surname=surname,
                other_names=other_names,
                id_number=id_number,
                phone_number=phone,
                email=email,
                date_of_birth=date_of_birth if date_of_birth else None,
                occupation=occupation,
                ethnicity=ethnicity,
                sex=sex,
                special_interest=special_interest,
                county=county_obj,
                constituency=constituency,
                ward=ward,
                polling_center=polling_center
            )
            # Store member ID in session for the success page
            request.session['new_member_id'] = member.id
            return redirect('join_success')
        except IntegrityError:
            messages.error(request, 'Comrade with this ID Number already registered!')
            counties = County.objects.all().order_by('name')
            return render(request, 'users/join.html', {'counties': counties})
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            counties = County.objects.all().order_by('name')
            return render(request, 'users/join.html', {'counties': counties})

    # GET request
    counties = County.objects.all().order_by('name')
    return render(request, 'users/join.html', {'counties': counties})

def join_coordinator(request):
    if request.method == "POST":
        # Personal Info
        surname = request.POST.get('surname')
        other_names = request.POST.get('other_names')
        full_name = f"{surname} {other_names}".strip()
        id_number = request.POST.get('id_number')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        date_of_birth = request.POST.get('date_of_birth')
        
        # Demographics
        occupation = request.POST.get('occupation')
        ethnicity = request.POST.get('ethnicity')
        sex = request.POST.get('sex')
        special_interest = request.POST.get('special_interest')
        
        # Location
        county_id = request.POST.get('county')
        constituency = request.POST.get('constituency')
        ward = request.POST.get('ward')
        polling_center = request.POST.get('polling_center')

        # Basic validation
        if not id_number or not phone or not surname:
            messages.error(request, 'Please fill all required fields')
            counties = County.objects.all().order_by('name')
            return render(request, 'users/join_coordinator.html', {'counties': counties})
            
        try:
            # Get County object if selected
            county_obj = None
            if county_id:
                try:
                    county_obj = County.objects.get(id=county_id)
                except County.DoesNotExist:
                    pass

            member = Member.objects.create(
                full_name=full_name,
                surname=surname,
                other_names=other_names,
                id_number=id_number,
                phone_number=phone,
                email=email,
                date_of_birth=date_of_birth if date_of_birth else None,
                occupation=occupation,
                ethnicity=ethnicity,
                sex=sex,
                special_interest=special_interest,
                county=county_obj,
                constituency=constituency,
                ward=ward,
                polling_center=polling_center,
                is_coordinator_applicant=True  # Mark as coordinator applicant
            )
            # Store member ID in session for the success page
            request.session['new_member_id'] = member.id
            return redirect('join_success')
        except IntegrityError:
            messages.error(request, 'Comrade with this ID Number already registered!')
            counties = County.objects.all().order_by('name')
            return render(request, 'users/join_coordinator.html', {'counties': counties})
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            counties = County.objects.all().order_by('name')
            return render(request, 'users/join_coordinator.html', {'counties': counties})

    # GET request
    counties = County.objects.all().order_by('name')
    return render(request, 'users/join_coordinator.html', {'counties': counties})

def check_id_number(request):
    id_number = request.GET.get('id_number')
    if id_number and Member.objects.filter(id_number=id_number).exists():
         return HttpResponse('<span class="text-roots-red font-bold uppercase block mt-1 bg-roots-black text-white p-2">⚠️ Error: Comrade already registered!</span>')
    return HttpResponse('')

@user_passes_test(lambda u: u.is_superuser)
def seed_members_view(request):
    try:
        target_count = 75000
        current_count = Member.objects.count()
        
        if current_count >= target_count:
            # Reset KPI on finish
            from core.models import PageContent
            try:
                pc = PageContent.objects.get(page_name='about')
                pc.kpi_value = None
                pc.save()
            except:
                pass
            return HttpResponse(f"""
                <h1 style='color:green'>DONE! Total Members: {current_count}</h1>
                <p>You can close this page.</p>
            """)

        # Insert batch of 1000
        batch_limit = 1000
        members = []
        
        # Calculate distinct start id for this batch based on current count
        # This is a heuristic; assumes sequential execution
        start_id = 70000000 + current_count 
        
        first_names = ['John', 'Jane', 'James', 'Mary', 'Peter', 'Grace', 'David', 'Faith', 'Joseph', 'Esther', 'Samuel', 'Mercy', 'Daniel', 'Joyce', 'Francis', 'Alice', 'George', 'Ann', 'Michael', 'Rose', 'Wanjiku', 'Otieno', 'Nanjala', 'Kipchoge', 'Kamau', 'Muthoni', 'Ochieng', 'Achieng', 'Wanyama', 'Nafula', 'Kimani', 'Nyambura', 'Odhiambo', 'Anyango', 'Kipkorir', 'Chebet', 'Maina', 'Njeri', 'Omondi', 'Akoth', 'Mutua', 'Mwende', 'Rotich', 'Chepkemoi', 'Njoroge', 'Wairimu', 'Okoth', 'Atieno', 'Kibet', 'Jepkorir']
        last_names = ['Kamau', 'Omondi', 'Kiptoo', 'Wanjiku', 'Juma', 'Odhiambo', 'Mutua', 'Wafula', 'Maina', 'Otieno', 'Kariuki', 'Njeri', 'Mwangi', 'Anyango', 'Njoroge', 'Wairimu', 'Kipkorir', 'Achieng', 'Kimani', 'Nyambura', 'Kibet', 'Chebet', 'Rotich', 'Chepkemoi', 'Koech', 'Jepchirchir', 'Kosgei', 'Jepkemboi', 'Cheruiyot', 'Cherono', 'Rono', 'Jepleting', 'Tanui', 'Jepkosgei', 'Lelei', 'Chepkoech', 'Mutai', 'Chepngeno', 'Lagat', 'Chelagat', 'Choge', 'Jepchumba', 'Sang', 'Chepchirchir', 'Kiprotich', 'Chepkirui', 'Korir', 'Chebet', 'Kirui', 'Chepkorir']

        for i in range(batch_limit):
            first = random.choice(first_names)
            last = random.choice(last_names)
            full_name = f"{first} {last}"
            id_number = str(start_id + i)
            phone = f"07{random.randint(10000000, 99999999)}"
            
            members.append(Member(full_name=full_name, id_number=id_number, phone_number=phone))
            
        Member.objects.bulk_create(members, ignore_conflicts=True)
        
        new_total = Member.objects.count()
        remaining = target_count - new_total
        
        return HttpResponse(f"""
            <h1>Seeding Progress...</h1>
            <p>Added 1,000 members.</p>
            <p><strong>Total: {new_total} / {target_count}</strong></p>
            <p>Remaining: {remaining}</p>
            <p><em>Auto-refreshing in 1 second to continue...</em></p>
            <script>
                setTimeout(function(){{ window.location.reload(); }}, 1000);
            </script>
        """)

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

def join_success(request):
    member_id = request.session.get('new_member_id')
    member = None
    if member_id:
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            pass
    return render(request, 'users/success.html', {'member': member})


def download_card(request, member_id):
    if not QRCODE_AVAILABLE:
        return HttpResponse("QR code library not installed. Please install 'qrcode[pil]' and 'reportlab' to use this feature.", status=500)
    
    try:
        member = Member.objects.get(id=member_id)
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Credit card size: 85.6mm x 53.98mm (3.375" x 2.125")
        card_width = 3.375 * inch
        card_height = 2.125 * inch
        
        # Create canvas
        c = canvas.Canvas(buffer, pagesize=(card_width, card_height))
        
        # Colors
        roots_red = colors.HexColor('#E60000')
        roots_black = colors.HexColor('#1a1a1a')
        
        # === BACKGROUND ===
        c.setFillColor(colors.white)
        c.rect(0, 0, card_width, card_height, fill=1, stroke=0)
        
        # === RED HEADER STRIPE ===
        header_height = 0.6 * inch
        c.setFillColor(roots_red)
        c.rect(0, card_height - header_height, card_width, header_height, fill=1, stroke=0)
        
        # === HEADER TEXT ===
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(0.15 * inch, card_height - 0.3 * inch, "ROOTS PARTY")
        c.setFont("Helvetica-Bold", 7)
        c.drawString(0.15 * inch, card_height - 0.45 * inch, "OFFICIAL MEMBERSHIP CARD")
        
        # === PARTY LOGO ===
        # Add logo to the right side of header
        try:
            logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'roots_logo_circle.png')
            logo_size = 0.5 * inch
            logo_x = card_width - logo_size - 0.15 * inch
            logo_y = card_height - header_height + (header_height - logo_size) / 2
            c.drawImage(logo_path, logo_x, logo_y, width=logo_size, height=logo_size, mask='auto')
        except Exception as e:
            # If logo fails to load, continue without it
            print(f"Warning: Could not load logo: {e}")
        
        # === MEMBER INFO SECTION ===
        y_pos = card_height - header_height - 0.2 * inch
        
        # Member ID Badge (small box)
        badge_width = 0.8 * inch
        badge_height = 0.25 * inch
        c.setFillColor(roots_black)
        c.rect(0.15 * inch, y_pos - badge_height, badge_width, badge_height, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(0.15 * inch + badge_width/2, y_pos - 0.09 * inch, "MEMBER")
        c.setFillColor(roots_red)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(0.15 * inch + badge_width/2, y_pos - 0.2 * inch, f"#{member.id}")
        
        y_pos -= 0.4 * inch
        
        # Name
        c.setFillColor(colors.HexColor('#666666'))
        c.setFont("Helvetica-Bold", 5)
        c.drawString(0.15 * inch, y_pos, "NAME")
        y_pos -= 0.12 * inch
        c.setFillColor(roots_black)
        c.setFont("Helvetica-Bold", 10)
        # Truncate name if too long
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
        
        # === QR CODE ===
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
        
        # Save QR to buffer
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # QR code size and position
        qr_size = 1.1 * inch
        qr_x = card_width - qr_size - 0.15 * inch
        qr_y = 0.25 * inch
        
        # Draw QR code background
        c.setFillColor(colors.HexColor('#f5f5f5'))
        c.setStrokeColor(roots_black)
        c.setLineWidth(2)
        c.rect(qr_x - 0.05 * inch, qr_y - 0.05 * inch, 
               qr_size + 0.1 * inch, qr_size + 0.1 * inch, 
               fill=1, stroke=1)
        
        # Draw QR code
        c.drawImage(ImageReader(qr_buffer), qr_x, qr_y, 
                    width=qr_size, height=qr_size, mask='auto')
        
        # "SCAN TO VERIFY" label
        c.setFillColor(roots_black)
        c.setFont("Helvetica-Bold", 5)
        c.drawCentredString(qr_x + qr_size/2, qr_y - 0.12 * inch, "SCAN TO VERIFY")
        
        # === FOOTER ===
        c.setFillColor(roots_black)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(card_width/2, 0.08 * inch, "TINGIZA MTI")
        
        # === BORDER ===
        c.setStrokeColor(roots_black)
        c.setLineWidth(3)
        c.rect(0, 0, card_width, card_height, fill=0, stroke=1)
        
        # Save PDF
        c.showPage()
        c.save()
        
        buffer.seek(0)
        
        return HttpResponse(buffer, content_type='application/pdf', headers={
            'Content-Disposition': f'attachment; filename="roots_party_card_{member.id_number}.pdf"',
        })
        
    except Member.DoesNotExist:
        return HttpResponse("Member not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error generating card: {str(e)}", status=500)
