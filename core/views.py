from .models import Leader, ManifestoItem

def home(request):
    return render(request, 'core/home.html')

def about(request):
    leaders = Leader.objects.all()
    return render(request, 'core/about.html', {'leaders': leaders})

def manifesto(request):
    items = ManifestoItem.objects.all()
    return render(request, 'core/manifesto.html', {'items': items})

from django.shortcuts import render, get_object_or_404

def manifesto_detail(request, slug):
    item = get_object_or_404(ManifestoItem, slug=slug)
    return render(request, 'core/manifesto_detail.html', {'item': item})

from .models import GalleryPost
def gallery(request):
    posts = GalleryPost.objects.prefetch_related('images').all()
    return render(request, 'core/gallery.html', {'posts': posts})

def leader_detail(request, slug):
    leader = get_object_or_404(Leader, slug=slug)
    return render(request, 'core/leader_detail.html', {'leader': leader})

def manifesto_list(request):
    # Simulate somewhat heavy load as requested
    # In reality this would be a DB query
    time.sleep(0.5) 
    commandments = [
        "Legalize Marijuana for Export",
        "Rearing Snakes for Venom Export",
        "Exporting Hyena Meat",
        "Hang the Corrupt",
        "Shut Down SGR",
        "4-Day Work Week",
        "Suspend the Constitution",
        "Move Capital to Isiolo",
        "Create 8 States",
        "Deport Idle Foreigners"
    ]
    return render(request, 'partials/manifesto_list.html', {'commandments': commandments})
