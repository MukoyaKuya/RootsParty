from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Vendor, Product, VendorApplication
from .forms import VendorReportForm, VendorApplicationForm


def shop(request):
    vendors = Vendor.objects.filter(is_active=True).prefetch_related('products')
    return render(request, 'core/shop_list.html', {'vendors': vendors})

def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, slug=vendor_slug, is_active=True)
    products = vendor.products.all()
    return render(request, 'core/vendor_detail.html', {'vendor': vendor, 'products': products})

def product_detail(request, vendor_slug, product_slug):
    vendor = get_object_or_404(Vendor, slug=vendor_slug, is_active=True)
    product = get_object_or_404(Product, slug=product_slug, vendor=vendor)
    
    # Get next and previous products from the same vendor
    all_products = list(vendor.products.all().order_by('id'))
    current_index = all_products.index(product)
    
    prev_product = all_products[current_index - 1] if current_index > 0 else None
    next_product = all_products[current_index + 1] if current_index < len(all_products) - 1 else None
    
    return render(request, 'core/product_detail.html', {
        'vendor': vendor, 
        'product': product,
        'prev_product': prev_product,
        'next_product': next_product
    })

def report_vendor(request, vendor_slug):
    vendor = get_object_or_404(Vendor, slug=vendor_slug, is_active=True)
    if request.method == 'POST':
        form = VendorReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.vendor = vendor
            report.save()
            messages.success(request, f"Your report for {vendor.name} has been sent. Please wait for a response in a few minutes.")
            return redirect('vendor_detail', vendor_slug=vendor.slug)
    else:
        form = VendorReportForm()
    
    return render(request, 'core/report_vendor.html', {
        'vendor': vendor,
        'form': form
    })

from core.models import County

def vendor_application(request):
    """View for handling new vendor registration applications."""
    if request.method == 'POST':
        form = VendorApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your application has been received! Our team will review your business and get in touch with you soon.")
            return redirect('shop')
    else:
        form = VendorApplicationForm()
    
    counties = County.objects.all().order_by('name')
    return render(request, 'core/vendor_application.html', {
        'form': form,
        'counties': counties,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
    })
