from django.shortcuts import render
from django.http import HttpResponse
from .models import Member

def join(request):
    if request.method == "POST":
        # Create member
        Member.objects.create(
            full_name=request.POST.get('full_name'),
            id_number=request.POST.get('id_number'),
            phone_number=request.POST.get('phone')
        )
        return render(request, 'users/success.html')
    return render(request, 'users/join.html')

def check_id_number(request):
    id_number = request.GET.get('id_number')
    if id_number and Member.objects.filter(id_number=id_number).exists():
         return HttpResponse('<span class="text-roots-red font-bold uppercase block mt-1 bg-roots-black text-white p-2">⚠️ Error: Comrade already registered!</span>')
    return HttpResponse('')
