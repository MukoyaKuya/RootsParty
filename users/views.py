from django.shortcuts import render
from django.http import HttpResponse
from .models import Member

def join(request):
    if request.method == "POST":
        # Create member
        # Basic validation
        if not request.POST.get('id_number') or not request.POST.get('phone'):
            return HttpResponse('<div class="text-roots-red font-bold">Please fill all fields</div>')
            
        Member.objects.create(
            full_name=request.POST.get('full_name'),
            id_number=request.POST.get('id_number'),
            phone_number=request.POST.get('phone')
        )
        
        # If HTMX, return just the success message content (we will create a partial or just toggle blocks)
        # But since we have success.html extending base, we need to be careful.
        # A simple fix if we don't have separate partials is to let it redirect or render.
        # For HTMX to work smoothly with full page templates, we usually use hx-target="body" or use a partial.
        # Let's assume we want to render the full success page for now, but cleaner.
        return render(request, 'users/success.html')
    return render(request, 'users/join.html')

def check_id_number(request):
    id_number = request.GET.get('id_number')
    if id_number and Member.objects.filter(id_number=id_number).exists():
         return HttpResponse('<span class="text-roots-red font-bold uppercase block mt-1 bg-roots-black text-white p-2">⚠️ Error: Comrade already registered!</span>')
    return HttpResponse('')
