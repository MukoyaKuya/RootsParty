from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Member, CoordinatorApplicant

@admin.register(Member)
class MemberAdmin(ModelAdmin):
    list_display = ('full_name', 'id_number', 'phone_number', 'county', 'created_at')
    list_filter = ('created_at', 'county')
    list_select_related = ('county',)
    search_fields = ('full_name', 'id_number', 'phone_number')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_coordinator_applicant=False)

    def save_model(self, request, obj, form, change):
        from core.cache_utils import invalidate_aspirant_cache
        super().save_model(request, obj, form, change)
        invalidate_aspirant_cache()

@admin.register(CoordinatorApplicant)
class CoordinatorApplicantAdmin(ModelAdmin):
    list_display = ('full_name', 'id_number', 'phone_number', 'county', 'created_at')
    list_filter = ('created_at', 'county')
    list_select_related = ('county',)
    search_fields = ('full_name', 'id_number', 'phone_number')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_coordinator_applicant=True)
