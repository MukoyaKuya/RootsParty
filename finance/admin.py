from django.contrib import admin
from .models import Donation

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'amount', 'transaction_reference', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('phone_number', 'transaction_reference')
