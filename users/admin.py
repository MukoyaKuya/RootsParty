from django.contrib import admin
from .models import Member, CoordinatorApplicant

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'id_number', 'phone_number', 'county', 'created_at')
    list_filter = ('created_at', 'county')
    search_fields = ('full_name', 'id_number', 'phone_number')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_coordinator_applicant=False)

@admin.register(CoordinatorApplicant)
class CoordinatorApplicantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'id_number', 'phone_number', 'county', 'created_at')
    list_filter = ('created_at', 'county')
    search_fields = ('full_name', 'id_number', 'phone_number')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_coordinator_applicant=True)
