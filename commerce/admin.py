from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Vendor, Product, VendorReport, VendorApplication

class ProductInline(TabularInline):
    model = Product
    extra = 1
    fields = ('name', 'slug', 'price', 'is_available', 'image')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Vendor)
class VendorAdmin(ModelAdmin):
    list_display = ('name', 'contact_email', 'is_active', 'is_verified', 'created_at')
    list_filter = ('is_active', 'is_verified', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'is_verified')
    inlines = [ProductInline]

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('name', 'vendor', 'price', 'is_available')
    list_filter = ('is_available', 'vendor')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(VendorReport)
class VendorReportAdmin(ModelAdmin):
    list_display = ('vendor', 'issue_type', 'email', 'created_at', 'is_resolved')
    list_filter = ('issue_type', 'is_resolved', 'created_at')
    search_fields = ('vendor__name', 'description', 'email')
    list_editable = ('is_resolved',)
    readonly_fields = ('created_at',)


@admin.register(VendorApplication)
class VendorApplicationAdmin(ModelAdmin):
    list_display = ('business_name', 'full_name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('business_name', 'full_name', 'email', 'phone_number', 'location')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'business_name', 'email', 'phone_number', 'location')
        }),
        ('Business Details', {
            'fields': ('product_categories', 'business_description', 'social_links')
        }),
        ('Status & Review', {
            'fields': ('status', 'notes', 'created_at')
        }),
    )
