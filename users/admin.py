from django.contrib import admin
from .models import Member

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'id_number', 'phone_number', 'created_at')
    search_fields = ('full_name', 'id_number', 'phone_number')
