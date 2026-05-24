import json
import logging
import uuid

from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from .services import MpesaService
from .models import Donation
from core.utils.validators import validate_kenyan_phone_number

logger = logging.getLogger(__name__)


def _get_client_ip(group, request):
    """Extract client IP (Cloud Run uses X-Forwarded-For)."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


@ratelimit(key=_get_client_ip, rate='10/m', block=True)
def donate(request):
    if request.method == "POST":
        phone_raw = request.POST.get('phone')
        amount_raw = request.POST.get('custom_amount') or request.POST.get('amount')
        try:
            phone = validate_kenyan_phone_number(phone_raw)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Please provide a valid Kenyan phone number.'}, status=400)
        
        # Validate amount
        try:
            from decimal import Decimal, InvalidOperation
            amount = Decimal(amount_raw)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (InvalidOperation, ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': 'Please provide a valid donation amount.'}, status=400)
        if amount > Decimal('250000'):
            return JsonResponse({'status': 'error', 'message': 'Donation amount is above the allowed limit.'}, status=400)
        
        # Trigger STK Push (Mock)
        reference = f"ROOTS-{uuid.uuid4().hex[:16].upper()}"
        success = MpesaService.trigger_stk_push(phone, amount, reference)
        
        if success:
            from django.db import transaction
            try:
                with transaction.atomic():
                    Donation.objects.create(
                        phone_number=phone,
                        amount=amount,
                        transaction_reference=reference,
                        status='PENDING' # In real life, we'd update this on callback
                    )
            except Exception:
                 logger.exception("Donation creation failed for reference %s", reference)
                 return JsonResponse({'status': 'error', 'message': 'Transaction failed internally.'}, status=500)
            
            return JsonResponse({'status': 'success', 'message': 'STK Push Sent! Check your phone.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to initiate payment.'}, status=400)
            
    return render(request, 'finance/donate.html')


@csrf_exempt
@require_POST
def mpesa_callback(request):
    configured_token = getattr(settings, 'MPESA_CALLBACK_TOKEN', '')
    if not configured_token:
        return JsonResponse({'status': 'error', 'message': 'Callback token not configured.'}, status=503)

    if request.headers.get('X-Roots-Callback-Token') != configured_token:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized callback.'}, status=403)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON.'}, status=400)

    reference = payload.get('transaction_reference') or payload.get('reference')
    status = (payload.get('status') or '').upper()
    if status not in {'COMPLETED', 'FAILED'}:
        return JsonResponse({'status': 'error', 'message': 'Invalid donation status.'}, status=400)

    updated = Donation.objects.filter(transaction_reference=reference).update(status=status)
    if not updated:
        return JsonResponse({'status': 'error', 'message': 'Donation not found.'}, status=404)

    return JsonResponse({'status': 'success'})
