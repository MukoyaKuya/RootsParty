from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop, name='shop'),
    path('apply/', views.vendor_application, name='vendor_application'),
    path('vendor/<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),
    path('vendor/<slug:vendor_slug>/report/', views.report_vendor, name='report_vendor'),
    path('vendor/<slug:vendor_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
]
