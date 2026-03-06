"""
Contact form and newsletter subscription views.
"""
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseNotAllowed
from django.shortcuts import render
from django.utils import timezone
from django_ratelimit.decorators import ratelimit

from ..forms import ContactForm, NewsletterForm
from ..models import ContactMessage, NewsletterSubscriber


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def contact(request):
    """Contact form view."""
    success = False

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data.get('phone', '')
            subject_choice = form.cleaned_data['subject']
            message_text = form.cleaned_data['message']

            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject_choice,
                message=message_text
            )

            subject_display = dict(form.fields['subject'].choices).get(subject_choice, subject_choice)
            email_subject = f"[Roots Party Contact] {subject_display} - from {name}"
            email_body = f"""
New contact form submission from Roots Party website:

Name: {name}
Email: {email}
Phone: {phone if phone else 'Not provided'}
Subject: {subject_display}

Message:
{message_text}

---
This message was sent from the Roots Party website contact form.
View all messages at: /admin/core/contactmessage/
            """

            try:
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else email,
                    [settings.CONTACT_EMAIL if hasattr(settings, 'CONTACT_EMAIL') else 'info@rootsparty.co.ke'],
                    fail_silently=True,
                )
            except Exception:
                pass

            if request.headers.get('HX-Request'):
                return render(request, 'partials/contact_success.html')
            
            success = True
            form = ContactForm()
        else:
            if request.headers.get('HX-Request'):
                return render(request, 'partials/contact_form.html', {'form': form})
    else:
        form = ContactForm()

    if request.headers.get('HX-Request') and request.method == 'GET':
        return render(request, 'partials/contact_form.html', {'form': form})

    return render(request, 'core/contact.html', {'form': form, 'success': success})


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def subscribe(request):
    """Newsletter subscription view (HTMX)."""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if 'rootsparty' in email and 'admin' in email:
                pass
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if created:
                try:
                    send_mail(
                        subject=f"[Roots Party Newsletter] New Subscriber: {email}",
                        message=f"New newsletter subscriber from website:\n\nEmail: {email}\n\nDate: {timezone.now()}",
                        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@rootsparty.co.ke',
                        recipient_list=[settings.CONTACT_EMAIL if hasattr(settings, 'CONTACT_EMAIL') else 'info@rootsparty.co.ke'],
                        fail_silently=True,
                    )
                except Exception:
                    pass
                return render(request, 'partials/subscribe_success.html', {'message': 'Subscribed successfully!'})
            else:
                return render(request, 'partials/subscribe_success.html', {'message': 'Already subscribed!'})
        else:
            return render(request, 'partials/subscribe_error.html', {'form': form})

    return HttpResponseNotAllowed(['POST'])
