from django.shortcuts import render
from django.http import JsonResponse
from .services import MpesaService
from .models import Donation

def donate(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        amount = request.POST.get('custom_amount') or request.POST.get('amount')
        
        # Trigger STK Push (Mock)
        success = MpesaService.trigger_stk_push(phone, amount)
        
        if success:
            from django.db import transaction
            try:
                with transaction.atomic():
                    Donation.objects.create(
                        phone_number=phone,
                        amount=amount,
                        status='PENDING' # In real life, we'd update this on callback
                    )
            except Exception as e:
                 return JsonResponse({'status': 'error', 'message': 'Transaction failed internally.'}, status=500)
            
            return JsonResponse({'status': 'success', 'message': 'STK Push Sent! Check your phone.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to initiate payment.'}, status=400)
            
    return render(request, 'finance/donate.html')
