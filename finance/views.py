from django.shortcuts import render
from django.http import JsonResponse
from .services import MpesaService

def donate(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        amount = request.POST.get('custom_amount') or request.POST.get('amount')
        
        # Trigger STK Push (Mock)
        success = MpesaService.trigger_stk_push(phone, amount)
        
        if success:
            return JsonResponse({'status': 'success', 'message': 'STK Push Sent! Check your phone.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to initiate payment.'}, status=400)
            
    return render(request, 'finance/donate.html')
