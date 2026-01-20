from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Donation

@admin.register(Donation)
class DonationAdmin(ModelAdmin):
    @display(
        description="Status",
        ordering="status",
        label={
            "PENDING": "Pending",
            "COMPLETED": "Completed",
            "FAILED": "Failed",
        }
    )
    def display_status(self, obj):
        return obj.status

    list_display = ('phone_number', 'amount', 'transaction_reference', 'display_status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('phone_number', 'transaction_reference')
